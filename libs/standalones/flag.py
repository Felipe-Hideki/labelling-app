class flags:
    def __init__(self, size: int):
        self.__size = size
        self.__flags: list[bool] = [False] * size

    def __getitem__(self, key: int) -> bool:
        assert key < self.__size
        return self.__flags[key]
    def __setitem__(self, key: int, value: bool) -> None:
        assert key < self.__size
        self.__flags[key] = value
    def __delitem__(self, key: int) -> None:
        assert key < self.__size
        del self.__flags[key]
    def __len__(self) -> int:
        return self.__size
    def __iter__(self):
        return iter(self.__flags)
    def __next__(self):
        return next(self.__flags)
    def __str__(self) -> str:
        text = ''
        for flag in self.__flags:
            text += str(int(flag))
        return text
    def __repr__(self) -> str:
        return self.__str__()
    
    def all_false(self) -> bool:
        return not self.__flags.__contains__(True)
    def all_true(self) -> bool:
        return not self.__flags.__contains__(False)
    def set(self, key: int, value: bool) -> None:
        self.__flags[key] = value
    def flip(self, key: int) -> None:
        self.__flags[key] = not self.__flags[key]