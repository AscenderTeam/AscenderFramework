from core.store.distributor import Distributor
from core.store.storage import BaseStore


def use_store(name: str) -> BaseStore | None:
    """
    ## Use store

    The hook is used to access the store from any place of code

    Args:
        name (str): Name of store

    Returns:
        BaseStore: Instance of store
    """
    try:
        return Distributor.get_store(name)

    except KeyError:
        return None