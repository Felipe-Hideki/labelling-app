from typing import Union
import keyboard
normalize_name = keyboard._canonical_names.normalize_name

class Key:
    def __init__(self, key: str = ""):
        self._char: str = ""
        self._mods: set[str] = set()

        self._raw_key = set(key.split('+'))
        self._raw_key = {normalize_name(k) for k in self._raw_key if k}
        
        self._formatted_key = ""

        for k in self._raw_key:
            if len(k) > 1:
                self._mods.add(k)
                continue
            if not self._char:
                self._char = k
        self.__update()

    def __update(self):
        self._formatted_key = keyboard.get_hotkey_name(self._raw_key)

    def get_char(self) -> str:
        return self._char
    
    def get_mods(self) -> set[str]:
        return set(self._mods)

    def get_formatted(self) -> str:
        return self._formatted_key

    def is_only_mods(self) -> bool:
        return not self._char

    def get_raw_key(self) -> list[str]:
        return list(self._raw_key)
    
    def set_key(self, key: str) -> None:
        key = normalize_name(key)

        if keyboard.is_modifier(key):
            self._mods.add(key)
            self._raw_key.add(key)
            self.__update()
            return
        if len(self._char) > 0:
            self._raw_key.remove(self._char)
        self._char = key
        self._raw_key.add(key)
        self.__update()

    def rem_key(self, mod: str = '') -> None:
        mod = normalize_name(mod) if mod else ''

        if keyboard.is_modifier(mod):
            self._mods.remove(mod)
            self._raw_key.remove(mod)
            self.__update()
            return
        self._char = ''
        if mod in self._raw_key:
            self._raw_key.remove(mod)
        self.__update()

    def __contains__(self, other: str) -> bool:
        return other in self.get_formatted()

    def __eq__(self, other: Union['Key', str]) -> bool:
        if isinstance(other, Key):
            return self.get_formatted() == other.get_formatted()
        if isinstance(other, str):
            return self.get_formatted() == normalize_name(other)
    
    def __str__(self) -> str:
        return self._formatted_key
    
    def __repr__(self) -> str:
        return self._formatted_key