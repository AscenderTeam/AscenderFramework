from typing import TypeVar, final
T = TypeVar("T")


class AbstractFactory:
    __module_factory: dict[type[T], T] = {}

    @final
    def factory_add(self, interface: type[T], instance: T):
        self.__module_factory[interface] = instance
    
    @final
    def factory_remove(self, interface: type[T]):
        del self.__module_factory[interface]
    
    def __factory__(self):
        return self.__module_factory