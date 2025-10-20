class UndefinedValue:
    """
    A class representing an undefined value in the CLI engine.
    This can be used to signify that a value has not been set or is not applicable.
    """
    def __init__(self) -> None:
        raise TypeError("UndefinedValue is an undefined type and cannot be instantiated.")
    
    def __repr__(self):
        return "UndefinedValue"

    def __bool__(self):
        return False

    def __eq__(self, other):
        return issubclass(other, UndefinedValue) or isinstance(other, UndefinedValue)

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __copy__(self):
        raise TypeError("UndefinedValue cannot be copied.")
    
    def __deepcopy__(self, memo):
        raise TypeError("UndefinedValue cannot be deep copied.")