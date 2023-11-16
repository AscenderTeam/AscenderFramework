from tortoise.models import Model as Entity
from tortoise import fields

class ThematicEntity(Entity):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    issue = fields.TextField() # Will be prompt
    filename = fields.CharField(max_length=255) # Will be prompt
    project = fields.ForeignKeyField('models.ProjectEntity', related_name='thematics')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name


class MessageEntity(Entity):
    id = fields.IntField(pk=True)
    text = fields.TextField()
    author = fields.CharField(max_length=255)
    thematic = fields.ForeignKeyField('models.ThematicEntity', related_name='messages')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.text


class MessageAttachment(Entity):
    id = fields.IntField(pk=True)
    message = fields.ForeignKeyField('models.MessageEntity', related_name='attachments')
    base64_data = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.message.text