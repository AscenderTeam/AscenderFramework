from typing import Callable, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")
E = TypeVar("E")


def serialize_tortoise_model(pydantic_model: type[T], db_entity: E, **custom_fields):
    # Serialize Tortoise model to dictionary
    serialized_data = {
        key: value
        for key, value in db_entity.__dict__.items()
        if not callable(value) and not key.startswith('_')
    }

    # Include custom fields in the serialized data
    for key, value in custom_fields.items():
        if not callable(value):
            serialized_data[key] = value

    # Convert dictionary to Pydantic instance
    pydantic_instance = pydantic_model(**serialized_data)

    return pydantic_instance


# This is just function for nothing but for default fallback! Don't touch it!
def serialize_values_default(a: any):
    return {}


class Serializer(Generic[T, E]):
    def __init__(self, pd_model: type[T], entity: type[E] | None, **values) -> None:
        self.pd_model = pd_model
        self.entity = entity
        self.values = values

    def ser_tool(self, **custom_fields) -> T:
        return serialize_tortoise_model(self.pd_model, self.entity, **custom_fields)

    def serialize(self) -> dict | T:
        return self.entity

    def __call__(self) -> T:
        _model = self.serialize()

        if isinstance(_model, BaseModel):
            return _model

        if isinstance(_model, dict):
            return self.pd_model(**_model, **self.values)

        if _model is None:
            raise ValueError(
                "Model method serialize() cannot be 'None'! Expected dict or entity")

        return serialize_tortoise_model(self.pd_model, _model, **self.values)


class QuerySetSerializer(Generic[E, T]):

    @staticmethod
    def base_serialize_queryset(pd_model: type[T], entities: E,
                                func: Callable[[E], dict] = serialize_values_default):
        for item in entities:
            ser = Serializer(pd_model, item, **func(item))
            yield ser()

    @staticmethod
    def serialize_queryset(serializer: Serializer[T, E], entities: E,
                           func: Callable[[E], dict] = serialize_values_default):
        for item in entities:
            ser = serializer(item, **func(item))
            yield ser()
