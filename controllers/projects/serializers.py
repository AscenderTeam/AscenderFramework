from controllers.common.models.pagination import PaginatedResponse
from controllers.projects.models import ProjectResponse
from core.extensions.serializer import Serializer
from entities.projects import ProjectEntity

class ProjectSerializer(Serializer):
    def __init__(self, entity: ProjectEntity) -> None:
        self.pd_model = ProjectResponse
        self.entity = entity
        self.values = {}

    def serialize(self) -> dict:
        return self.entity

class PaginationSerializer(Serializer):
    def __init__(self,
                 total: int, current_page: int, page_size: int, entities: list[ProjectResponse]) -> None:
        self.pd_model = PaginatedResponse[ProjectResponse]
        self.values = {
            "total": total,
            "current_page": current_page,
            "page_size": page_size,
            "results": [ProjectSerializer(entity)() for entity in entities]
        }
        self.entity = None

    def serialize(self) -> dict:
        return {}