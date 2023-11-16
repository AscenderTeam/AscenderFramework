from controllers.thematics.models import ThematicResponse
from core.extensions.serializer import Serializer
from entities.dialogue import ThematicEntity

class ThematicSerializer(Serializer):
    def __init__(self, entity: ThematicEntity) -> None:
        self.pd_model = ThematicResponse
        self.entity = entity
        self.values = {}

    def serialize(self) -> dict:
        return self.entity