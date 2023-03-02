import keyboard
import json
import os.path

from PyQt5.QtWidgets import QMainWindow

KEY_DOWN = 0
KEY_UP = 1

class bind:
    def __init__(self, key: str, state_type: int, toggle: bool, funcs: list[any] = [], state: bool = False):
        self.key = key
        self.scancode = keyboard.key_to_scan_codes(key)[0]
        self.state_type = state_type
        self.toggle = toggle
        self.funcs = list(funcs)
        self.state = state

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
        self.__mainWindow = mainWindow

        if not os.path.exists(self.__keybinds_path) and not os.path.exists(self.__default_keybinds_path):
            self.__binds: dict[str, bind] = {
            "create-shape": bind('w', KEY_DOWN, False),
            "delete-shape": bind('delete', KEY_DOWN, False),
            "multi-select": bind('control', KEY_DOWN, True)
            }
            self.save()
            return
        elif os.path.exists(self.__keybinds_path):
            with open(self.__keybinds_path, 'r') as f:
                binds = json.load(f)
        elif os.path.exists(self.__default_keybinds_path):
            with open(self.__default_keybinds_path, 'r') as f:
                binds = json.load(f)
        
        self.__binds: dict[str, bind] = {}

        for key, val in binds.items():
            print(val)
            self.__binds[key] = bind(val['key'], val['state_type'], val['toggle'])

        self.__binds: dict[str, bind] = {
            "create-shape": bind('w', KEY_DOWN, False),
            "delete-shape": bind('delete', KEY_DOWN, False),
            "multi-select": bind('control', KEY_DOWN, True)
        }

        keyboard.hook(self.__hook)

    # TODO: Change name of this function
    def __broadcast(self, funcs: list[any]) -> None:
        for func in funcs:
            func()

    def __hook(self, event: keyboard.KeyboardEvent) -> None:
        if event.event_type == keyboard.KEY_DOWN:
            self.__on_key_press(event)
        elif event.event_type == keyboard.KEY_UP:
            self.__on_key_up(event)

    def __on_key_press(self, event: keyboard.KeyboardEvent) -> None:
        if not self.__mainWindow.isActiveWindow():
            return

        for bind_details in self.__binds.values():
            if bind_details.state_type == KEY_DOWN \
                    and not bind_details.state and bind_details.scancode == event.scan_code:
                self.__broadcast(bind_details.funcs)
                bind_details.state = True

    def __on_key_up(self, event: keyboard.KeyboardEvent) -> None:
        if not self.__mainWindow.isActiveWindow():
            for bind_details in self.__binds.values():
                if bind_details.state and bind_details.key == event.name:
                    bind_details.state = False
            return
        for bind_details in self.__binds.values():
            if (bind_details.state_type == KEY_UP or bind_details.toggle) and bind_details.scancode == event.scan_code:
                self.__broadcast(bind_details.funcs)
            if bind_details.state and bind_details.scancode == event.scan_code:
                bind_details.state = False

    def bind_to(self, action: str, func: any) -> None:
        '''
        Binds a function to a key press.

        Args:
            action (str): The action to bind to.
            func (any): The function to bind.
        '''
        self.__binds[action].funcs.append(func)
        
    def unbind(self, action: str, func: any) -> None:
        '''
        Unbinds a function from a key press.

        Args:
            action (str): The action to unbind from.
            func (any): The function to unbind.
        '''
        self.__binds[action].funcs.remove(func)

    def modify_bind(self, action: str, key: str, state_type: int, toggle: bool) -> None:
        '''
        Modifies a action's keybind. This will not unbind the old keybind.

        Args:
            action (str): The action to modify.
            key (str): The new key to bind to.
            state_type (int): Call when key is down or up.
            toggle (bool): Call on both key down and up.
        '''
        if action not in self.__binds:
            return
        self.__binds[action].key = key
        self.__binds[action].state_type = state_type
        self.__binds[action].toggle = toggle

    def change_key(self, action: str, key: str) -> None:
        self.modify_bind(action, key, self.__binds[action].state_type, self.__binds[action].toggle)

    def add_bind(self, action: str, key: str, state_type: int, toggle: bool) -> None:
        '''
        Adds a new keybind.

        Args:
            action (str): The action to bind to.
            key (str): The key to bind to.
            state_type (int): Call when key is down or up.
            toggle (bool): Call on both key down and up.
        '''
        if action in self.__binds:
            return
        self.__binds[action] = bind(key, state_type, toggle)

    def save(self):
        data: dict[str, dict[str, bind]] = {}
        for key, val in self.__binds.items():
            data[key] = {
                "key": val.key,
                "state_type": val.state_type,
                "toggle": val.toggle
            }

        with open(self.__keybinds_path, 'w') as file:
            json.dump(data, file, indent=4)

        if not os.path.exists(self.__default_keybinds_path):
            with open(self.__default_keybinds_path, 'w') as file:
                json.dump(data, file, indent=4)