import os
import json
from enum import Enum

class PersistentDataType(Enum):
    last_folder = 0

    def __str__(self):
        return self.name

class PersistentData:
    __instance = None

    _save_folder = "./Settings"
    _save_path = "./Settings/PersistentData.stg"

    @classmethod
    def instance(cls) -> 'PersistentData':
        return cls.__instance
    
    def __init__(self):
        self.__settings: dict[PersistentDataType, any] = {}

        try:
            self.load()
        except json.JSONDecodeError:
            self.__save_default()
        finally:
            self.load()

        PersistentData.__instance = self

    def __getitem__(self, key: PersistentDataType) -> any:
        return self.__settings[key]

    def __setitem__(self, key: PersistentDataType, val: any):
        self.__settings[key] = val

    def __len__(self) -> int:
        return len(self.__settings)
    
    def __save_default(self):
        os.makedirs(PersistentData._save_folder, exist_ok=True)

        default_values = \
        {
            str(PersistentDataType.last_folder): ""
        }

        with open(PersistentData._save_path, 'w') as f:
            json.dump(default_values, f, indent=4)

    def __json_friendly(self, settings: dict[PersistentDataType, any] = None) -> dict[str, any]:
        if settings is None:
            settings = self.__settings
        
        formatted: dict[str, any] = {}

        for key, value in settings.items():
            formatted[str(key)] = value
        
        return formatted
    
    def load(self):
        if not os.path.exists(PersistentData._save_path):
            self.__save_default()
        
        with open(PersistentData._save_path, 'r') as f:
            settings: dict[str, any] = json.load(f)
        
        for key, val in settings.items():
            self.__settings[PersistentDataType[key]] = val
        
    def save(self):
        if not os.path.exists(PersistentData._save_path):
            os.makedirs(PersistentData._save_folder, exist_ok=True)

        formatted = self.__json_friendly()
        
        with open(PersistentData._save_path, 'w') as f:
            json.dump(formatted, f, indent=4)