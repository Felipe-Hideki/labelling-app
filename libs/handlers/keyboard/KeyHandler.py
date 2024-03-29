import keyboard
import json
import os
import platform
import typing

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QThreadPool, QRunnable

from libs.handlers.keyboard.Bind import bind
from libs.handlers.keyboard.ActionBind import ActionBind
from libs.handlers.keyboard.Key import Key
from libs.handlers.keyboard.KeyStates import KeyStates
from libs.handlers.keyboard.KeyHandlerWin import KeyHandlerWin

def save_folder() -> str:
    return './Settings/Keybinds'

class KeyHandler:
    '''
    Singleton class for handling key presses. It needs to be instantialized before calling instance().

    Usage:
        keyHandler.instance().bind_to("action", func)
    '''
    __instance: 'KeyHandler' = None

    __default_keybinds_path = f'{save_folder()}/default_keybinds.json'
    __keybinds_path = f'{save_folder()}/keybinds.json'
    
    @classmethod
    def instance(cls: 'KeyHandler') -> typing.Union['KeyHandler', KeyHandlerWin]:
        '''
            Returns the instance of the class. None if no instances was created.
        '''
        return cls.__instance if platform.system() != "Windows" else KeyHandlerWin.instance()

    def __new__(cls: 'KeyHandler', mainWindow: QMainWindow) -> 'KeyHandler':
        if platform.system() == "Windows":
            if not KeyHandlerWin.instance():
                KeyHandlerWin(mainWindow)
            return KeyHandlerWin.instance()
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
            cls.__instance.__load(mainWindow)
        return cls.__instance
    
    def __init__(self, mainWindow: QMainWindow) -> None: ...

    def __load(self, mainWindow: QMainWindow) -> None:
        self.__changed_key = ""
        self.__mainWindow = mainWindow
        self.lost_focus = False
        self.global_thread = QThreadPool.globalInstance()

        if not os.path.exists(save_folder()):
            os.makedirs(save_folder())

        if not os.path.exists(self.__keybinds_path) and not os.path.exists(self.__default_keybinds_path):
            self.__binds: dict[str, bind] = {
            ActionBind.next_image: bind(Key('d'), KeyStates.KEY_DOWN, False),
            ActionBind.prev_image: bind(Key('a'), KeyStates.KEY_DOWN, False),
            ActionBind.create_shape: bind(Key('w'), KeyStates.KEY_DOWN, False),
            ActionBind.delete_shape: bind(Key('delete'), KeyStates.KEY_DOWN, False),
            ActionBind.multi_select: bind(Key('control'), KeyStates.KEY_CHANGE, True),
            ActionBind.move: bind(Key('space'), KeyStates.KEY_DOWN, True),
            ActionBind.edit: bind(Key('control+e'), KeyStates.KEY_DOWN, False)
            }
            self.save()
        if os.path.exists(self.__keybinds_path):
            with open(self.__keybinds_path, 'r') as f:
                binds: dict[str, str] = json.load(f)
        elif os.path.exists(self.__default_keybinds_path):
            with open(self.__default_keybinds_path, 'r') as f:
                binds: dict[str, str] = json.load(f)
        
        self.__binds: dict[str, bind] = {}

        for key, val in binds.items():
            self.__binds[ActionBind[key]] = bind(Key(val['key']), KeyStates[val['state_type']], val['toggle'])

        keyboard.hook(self.__hook)

    # TODO: Change name of this function
    def __broadcast(self, runnable: QRunnable) -> None:
        self.global_thread.start(runnable)

    def __hook(self, event: keyboard.KeyboardEvent) -> None:
        
        if event.event_type == keyboard.KEY_DOWN:
            self.__on_key_press(event)
        elif event.event_type == keyboard.KEY_UP:
            self.__on_key_up(event)
        
        self.lost_focus = False

    def __on_key_press(self, event: keyboard.KeyboardEvent) -> None:
        if not self.__mainWindow.isActiveWindow():
            return
        
        print(f"mod: {event.modifiers}")
        
        keys_pressed = ""
        if event.modifiers is not None:
            for mod in event.modifiers:
                keys_pressed += f'{mod}+'
        keys_pressed += event.name

        for bind_details in self.__binds.values():
            if bind_details.state_type == KeyStates.KEY_CHANGE and not bind_details.state \
                    and keys_pressed == bind_details.key:
                self.__broadcast(bind_details.runnable)
                bind_details.state = True
                continue

            if bind_details.state_type == KeyStates.KEY_DOWN and not bind_details.state \
                    and keys_pressed == bind_details.key:
                self.__broadcast(bind_details.runnable)
                bind_details.state = True

    def __on_key_up(self, event: keyboard.KeyboardEvent) -> None:
        keys_pressed = ""
        removed = event.name

        for mod in event.modifiers:
            keys_pressed += f'{mod}+'
        if not keyboard.is_modifier(removed):
            keys_pressed += removed
        else:
            keys_pressed = keys_pressed.removesuffix("+")

        for bind_details in self.__binds.values():
            if bind_details.state_type == KeyStates.KEY_CHANGE and bind_details.state \
                    and (bind_details.key == keys_pressed or removed in bind_details.key):
                self.__broadcast(bind_details.runnable)
                bind_details.state = False
                continue

            if (bind_details.state_type == KeyStates.KEY_UP or (bind_details.toggle and bind_details.state)) \
                    and (bind_details.key == keys_pressed or removed in bind_details.key):
                self.__broadcast(bind_details.runnable)
                bind_details.state = False
            if bind_details.state and self.__changed_key in bind_details.key:
                bind_details.state = False

    def bind_to(self, action: str, func: any) -> None:
        '''
        Binds a function to a key press.

        Args:
            action (str): The action to bind to.
            func (any): The function to bind.
        '''
        self.__binds[action].add_func(func)
        
    def unbind(self, action: str, func: any) -> None:
        '''
        Unbinds a function from a key press.

        Args:
            action (str): The action to unbind from.
            func (any): The function to unbind.
        '''
        self.__binds[action].funcs.remove(func)

    def modify_bind(self, action: str, key: Key, state_type: int, toggle: bool) -> None:
        '''
        Modifies a action's keybind. This will not unbind the old keybind.

        Args:
            action (str): The action to modify.
            key (str): The new key to bind to.
            state_type (int): Call when key is down or up.
            toggle (bool): Call on both key down and up.
        '''
        assert type(key) == Key, "key must be of type Key"
        if action not in self.__binds:
            return
        self.__binds[action].key = key
        self.__binds[action].state_type = state_type
        self.__binds[action].toggle = toggle

    def change_key(self, action: str, key: Key) -> None:
        self.modify_bind(action, key, self.__binds[action].state_type, self.__binds[action].toggle)

    def save(self):
        data: dict[str, dict[str, bind]] = {}
        for key, val in self.__binds.items():
            data[str(key)] = {
                "key": str(val.key),
                "state_type": str(val.state_type),
                "toggle": val.toggle
            }

        with open(self.__keybinds_path, 'w') as file:
            json.dump(data, file, indent=4)

        if not os.path.exists(self.__default_keybinds_path):
            with open(self.__default_keybinds_path, 'w') as file:
                json.dump(data, file, indent=4)