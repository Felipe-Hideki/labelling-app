from inspect import currentframe

def get_line_num() -> int:
    cf = currentframe()
    return cf.f_back.f_lineno

class baseException(Exception):
    def __init__(self, inner: str = None) -> None:
        super().__init__(None)
        self.inner = inner

    def _exception_info(self) -> str:
        return "Basic Exception"

    def __repr__(self) -> str:
        return f"{__class__.__name__}\nException info: {self._exception_info()}. At line {get_line_num()}\nInnerException: {self.inner}"

class ShapeNoPointsException(baseException):
    def _exception_info(self) -> str:
        return "Tried to use Shape that has no points to draw"

class InvalidVertexException(baseException):
    def _exception_info(self) -> str:
        return "Tried to access a invalid vertex from shape"

class InvalidInstantiation(baseException):
    def _exception_info(self) -> str:
        return "Tried to instantiate a invalid class"