from __future__ import annotations
from typing import TYPE_CHECKING, Any
from core.store.storage import BaseStore

if TYPE_CHECKING:
    from core.application import Application


class Distributor:
    stores: dict[str, list[BaseStore | any]] = {}

    @staticmethod
    def register_store(name: str, store: BaseStore) -> None:
        Distributor.stores[name] = store
    
    @staticmethod
    def get_store(name: str) -> BaseStore:
        return Distributor.stores[name]
    
    @staticmethod
    def get_stores() -> dict[str, BaseStore]:
        return Distributor.stores
    
    @staticmethod
    def create_base_store(default_values: Any):
        return BaseStore(default_values)