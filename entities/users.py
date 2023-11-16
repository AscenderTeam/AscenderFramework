from typing import Optional
from tortoise.models import Model as Entity
from tortoise import fields

class UserEntity(Entity):
    id: int = fields.IntField(pk=True)
    username: str = fields.CharField(max_length=255)
    email: str = fields.CharField(max_length=100, unique=True)
    password: str = fields.TextField()
    is_active: bool = fields.BooleanField(default=False)

    def __str__(self):
        return self.username

class GithubUserEntity(Entity):
    id: int = fields.IntField(pk=True)
    login: str = fields.CharField(max_length=255)
    access_token: str = fields.CharField(max_length=255, unique=True)
    label: Optional[str] = fields.CharField(max_length=255, null=True)

    def __str__(self):
        return self.login