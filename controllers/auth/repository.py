# from entities.[your_entity] import [YourEntity]Entity
from core.extensions.authentication.entity import UserEntity
from core.extensions.repositories import Repository


class AuthRepo(Repository):
    def __init__(self) -> None:
        """
        Define your repository here

        Name of entities that were set in `def setup()` in endpoints.py file are will passed into __init__ here
        Note that if you are not using entities that were added in `def setup()` then remove it from there also, or else you will receive error
        """
        # def __init__(self, [your_entity]: YourEntity]Entity) -> None:
        #   self.[your_entity] = [your_entity]

    async def update_user_from_entity(self, entity: UserEntity, **kwargs) -> UserEntity:
        """
        Update user from entity

        :param entity: UserEntity
        :param kwargs: Any
        :return: UserEntity
        """
        query = entity.update_from_dict(kwargs)

        await query.save()
        return query
    
    async def delete_user(self, entity: UserEntity):
        """
        Delete user

        :param user_id: str
        :return: bool
        """
        return await entity.delete()