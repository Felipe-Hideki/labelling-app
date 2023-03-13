import keyboard
import json
import os.path
from enum import Enum

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QRunnable, QThreadPool

class test(QRunnable):
    def __init__(self, funcs: set[any]):
        super().__init__()
        self.funcs = funcs

        self.setAutoDelete(False)

    def run(self):
        for func in self.funcs:
            func()

class keyStates(Enum):
    KEY_DOWN = 0
    KEY_UP = 1
    KEY_CHANGE = 2

    def __str__(self) -> str:
        return self.name

class ActionBind(Enum):
    next_image = 0
    prev_image = 1
    create_shape = 2
    delete_shape = 3
    multi_select = 4
    move = 5
    edit = 6

    def __str__(self) -> str:
        return self.name

class Key:
    def __init__(self, key: str):
        self.__key_str = key
        self.keys: set[str] = set()
        for k in key.split('+'):
            self.keys.add(keyboard._canonical_names.normalize_name(k))

    def __contains__(self, val: str) -> bool:
        return val in self.keys
    
    def __str__(self) -> str:
        return self.__key_str

    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other: set[str]) -> bool:
        return self.keys == other

class bind:
    def __init__(self, key: Key, state_type: keyStates, toggle: bool, funcs: list[any] = [], state: bool = False):
        self.key = key
        self.state_type = state_type
        self.toggle = toggle
        self.funcs = set(funcs)
        self.state = state
        self.runnable = test(self.funcs)

    def add_func(self, func: any):
        self.funcs.add(func)
        self.runnable.funcs.add(func)

class keyHandler:
    '''
    Singleton class for handling key presses. It needs to be instantialized before calling instance().

    Usage:
        keyHandler.instance().bind_to("action", func)
    '''
    __instance = None

    __default_keybinds_path = './default_keybinds.json'
    __keybinds_path = './keybinds.json'
    
    @classmethod
    def instance(cls: 'keyHandler') -> 'keyHandler':
        '''
            Returns the instance of the class. None if no instances was created.
        '''
        return cls.__instance

    def __new__(cls: 'keyHandler', mainWindow: QMainWindow) -> 'keyHandler':
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
            cls.__instance.__load(mainWindow)
        return cls.__instance
    
    def __init__(self, mainWindow: QMainWindow) -> None: ...

    def __load(self, mainWindow: QMainWindow) -> None:
        self.__keys_pressed: set[str] = set()
        self.__changed_key = ""
        self.__mainWindow = mainWindow
        self.lost_focus = False
        self.global_thread = QThreadPool.globalInstance()

        if not os.path.exists(self.__keybinds_path) and not os.path.exists(self.__default_keybinds_path):
            self.__binds: dict[str, bind] = {
            ActionBind.next_image: bind(Key('d'), keyStates.KEY_DOWN, False),
            ActionBind.prev_image: bind(Key('a'), keyStates.KEY_DOWN, False),
            ActionBind.create_shape: bind(Key('w'), keyStates.KEY_DOWN, False),
            ActionBind.delete_shape: bind(Key('delete'), keyStates.KEY_DOWN, False),
            ActionBind.multi_select: bind(Key('control'), keyStates.KEY_CHANGE, True),
            ActionBind.move: bind(Key('space'), keyStates.KEY_DOWN, True),
            ActionBind.edit: bind(Key('control+e'), keyStates.KEY_DOWN, False)
            }
            self.save()
        if os.path.exists(self.__keybinds_path):
            with open(self.__keybinds_path, 'r') as f:
                binds = json.load(f)
        elif os.path.exists(self.__default_keybinds_path):
            with open(self.__default_keybinds_path, 'r') as f:
                binds = json.load(f)
        
        self.__binds: dict[str, bind] = {}

        for key, val in binds.items():
            self.__binds[ActionBind[key]] = bind(Key(val['key']), keyStates[val['state_type']], val['toggle'])

        keyboard.hook(self.__hook)

    # TODO: Change name of this function
    def __broadcast(self, runnable: QRunnable) -> None:
        self.global_thread.start(runnable)

    def __reset_keys(self):
        for bind_details in self.__binds.values():
            bind_details.state = False

    def __hook(self, event: keyboard.KeyboardEvent) -> None:
        if not self.__mainWindow.isActiveWindow():
            self.__keys_pressed.clear()
            if not self.lost_focus:
                self.__reset_keys()
            self.lost_focus = True
            return
        self.__changed_key = event.name

        if event.event_type == keyboard.KEY_DOWN:
            self.__keys_pressed.add(event.name)
            self.__on_key_press(event)
        elif event.event_type == keyboard.KEY_UP:
            self.__on_key_up(event)
            if not self.lost_focus:
                self.__keys_pressed.remove(event.name)
        
        self.lost_focus = False

    def __on_key_press(self, event: keyboard.KeyboardEvent) -> None:
        for bind_details in self.__binds.values():
            if bind_details.state_type == keyStates.KEY_CHANGE and bind_details.key == self.__keys_pressed:
                if not bind_details.state:
                    self.__broadcast(bind_details.runnable)
                    bind_details.state = True
                continue

            if bind_details.state_type == keyStates.KEY_DOWN and not bind_details.state \
                    and self.__changed_key in bind_details.key and bind_details.key == self.__keys_pressed:
                self.__broadcast(bind_details.runnable)
                bind_details.state = True

    def __on_key_up(self, event: keyboard.KeyboardEvent) -> None:
        for bind_details in self.__binds.values():
            if bind_details.state_type == keyStates.KEY_CHANGE and bind_details.key == self.__keys_pressed:
                if bind_details.state:
                    self.__broadcast(bind_details.runnable)
                    bind_details.state = False
                continue

            if (bind_details.state_type == keyStates.KEY_UP or (bind_details.toggle and bind_details.state)) \
                    and self.__keys_pressed == bind_details.key and self.__changed_key in bind_details.key:
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