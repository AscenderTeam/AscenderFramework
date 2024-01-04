from __future__ import annotations
from typing import TYPE_CHECKING
from core.store.storage import BaseStore

if TYPE_CHECKING:
    from core.application import Application


class Distributor:
    stores: dict[str, list[BaseStore | any]] = {}

    @staticmethod
    def register_store(app: Application, name: str, store: BaseStore) -> None:
        if not isinstance(app, Application):
            raise TypeError("You need an instance of app")
        
        Distributor.stores[name] = store
    
    @staticmethod
    def get_store(name: str) -> BaseStore:
        return Distributor.stores[name]
    
    @staticmethod
    def get_stores() -> dict[str, BaseStore]:
        return Distributor.stores