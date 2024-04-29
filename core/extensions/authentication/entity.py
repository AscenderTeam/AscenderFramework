from tortoise.models import Model as Entity
from tortoise import fields

class UserEntity(Entity):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=128)
    email = fields.CharField(max_length=128, null=True)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self) -> str:
        return self.username

# class SessionEntity(Entity):
#     id = fields.IntField(pk=True)
#     user = fields.ForeignKeyField('models.UserEntity', related_name='sessions')
#     token = fields.CharField(max_length=128, unique=True)
#     expires_at = fields.DatetimeField(null=True)
#     created_at = fields.DatetimeField(auto_now_add=True)
#     updated_at = fields.DatetimeField(auto_now=True)

#     def __str__(self) -> str:
#         return self.token