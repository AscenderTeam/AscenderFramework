from tortoise.models import Model as Entity
from tortoise import fields

class ProjectEntity(Entity):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    github_url = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class ProjectDockerEntity(Entity):
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField('models.ProjectEntity', related_name='project_dockers')
    container_name = fields.CharField(max_length=255)
    container_id = fields.TextField(null=True)

    def __str__(self):
        return self.container_name


class ProjectStructureEntity(Entity):
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField('models.ProjectEntity', related_name='project_structures')
    data = fields.JSONField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.project.name