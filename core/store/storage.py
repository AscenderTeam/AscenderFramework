from typing import Callable, TypeVar, Generic, overload

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseStore(Generic[T]):
    __states: T

    def __init__(self, default_values: T) -> None:
        self.__states = default_values
        self.__watchers: list[Callable[[T, T], None]] = []
    
    @overload
    def get(self, filter: Callable[[T], any] | None = None) -> T:
        ...
    
    @overload
    def get(self) -> T:
        ...
    
    def get(self, filter: Callable[[T], any] | None = None) -> T:
        """
        Made for pydantic only
        """
        if filter is None:
            return self.__states
        
        return filter(self.__states)
    
    def set(self, value: T) -> None:
        self.__execute_watchers(self.__states, value)
        self.__states = value

    def watch(self, callback: Callable[[T, T], None]) -> None:
        self.__watchers.append(callback)

    def __execute_watchers(self, old_value: T, new_value: T) -> None:
        for watcher in self.__watchers:
            watcher(old_value, new_value)
    