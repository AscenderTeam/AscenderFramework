# from entities.[your_entity] import [YourEntity]Entity
from core.extensions.repositories import Repository


class AppRepo(Repository):
    def __init__(self) -> None:
        """
        Define your repository here

        Name of entities that were set in `def setup()` in endpoints.py file are will passed into __init__ here
        Note that if you are not using entities that were added in `def setup()` then remove it from there also, or else you will receive error
        """
        # def __init__(self, [your_entity]: YourEntity]Entity) -> None:
        #   self.[your_entity] = [your_entity]
