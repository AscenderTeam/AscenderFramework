from typing import overload
from start import app

def use_loader():
    """
    ## Loader hook

    Loader module hook can be called from any places of code
    Hook was made to access the framework core loader information
    Information about controllers and also ability to load controller from other place of code
    Also it contains instances of controllers which can be used inside of dependencies

    Returns:
        Loader: Instance of app loader module
    """
    return app.loader_module

@overload
def use_controllers() -> list[object]:
    """
    ## Use controllers hook

    Commonly made for dependency injections. But can be used in otehr places of code.
    This hook contains instances of loaded controllers

    Returns:
        list[object]: List of controller instances
    """
    ...

@overload
def use_controllers(_name: str = "") -> object | None:
    """
    ## Use controllers hook

    Commonly made for dependency injections. But can be used in otehr places of code.
    This hook contains instances of loaded controllers

    Args:
        _name: Name of the specific controller

    Returns:
        object: Specific controller instance
    """

def use_controllers(_name: str = ""):
    # Available controllers
    __controllers = app.loader_module._active_controllers
    
    if _name:
        __controller = next((item for item in __controllers if item.__class__.__name__ == _name), None)
    
    return __controller if _name else __controllers