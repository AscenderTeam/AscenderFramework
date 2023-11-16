from typing import Optional, overload
from core.extensions.repositories import Repository
from tortoise.models import Model as Entity



class Service:
    def __init__(self, repository: Repository) -> None:
        self._repository = repository
    
    @overload
    def inject_controller(self, controller: str): ...

    @overload
    def inject_controller(self, controller: str, name: Optional[str] = None, modules: tuple[str] = []): ...

    def inject_controller(self, controller: str, name: Optional[str] = None, modules: tuple[str] = []):
        _controllers = list(map(lambda c: c.__class__.__name__, self._loader._active_controllers))
        _controller_index = _controllers.index(controller)
        __controller: object = self._loader._active_controllers[_controller_index]

        if not name:
            name = __controller.__class__.__name__.lower()
        
        setattr(self, name, __controller) 

    @overload
    def append_repository(self, name: str | None, repository: Repository): ...

    @overload
    def append_repository(self, name: str | None, repository: Repository, _suffix: str = "Repo"): ...
    
    @overload
    def append_repository(self, name: str | None, repository: Repository, _suffix: str = "Repo", entities: dict[str, Entity] = {}): ...

    def append_repository(self, name: str | None, repository: type[Repository], _suffix: str = "Repo", entities: dict[str, Entity] = {}) -> None:
        repository_instance = repository(**entities)
        
        if name:
            setattr(self, f'_{name}', repository_instance)
            return
        
        setattr(self, f"_{repository.__class__.__name__.lower().removesuffix(_suffix)}", repository_instance)