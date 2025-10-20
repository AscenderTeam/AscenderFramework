import random
import string
import uuid
from datetime import datetime, date, time
from enum import Enum
from types import UnionType
from typing import (
    Annotated, Any, Callable, Sequence, TypeVar, Union, cast, get_args, get_origin, List, Literal
)
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from ascender.testing.utils.metadata.faker_field import FakerField

try:
    from faker import Faker
    _faker = Faker()
except ImportError:
    _faker = None


BM = TypeVar("BM", bound=BaseModel)
T = TypeVar("T")


# --- Utilities ------------------------------------------------------------

def issubclass_safe(cls, class_or_tuple) -> bool:
    """Safe version of issubclass that returns False if the first arg isn't a class."""
    try:
        return issubclass(cls, class_or_tuple)
    except TypeError:
        return False


# --- Mixer ---------------------------------------------------------------

class Mixer:
    """
    Pydantic model data generator with optional Faker integration and
    auto-inference by field name.

    Args:
        extra_generators: Mapping of custom generators (type → callable).
        enable_auto_faker: if True, guesses faker generator from field name.
        extra_faker_map: additional field name→faker method mapping.
    """

    def __init__(
        self,
        extra_generators: dict[Any, Callable[..., Any]] | None = None,
        enable_auto_faker: bool = False,
        extra_faker_map: dict[str, str] | None = None,
    ):
        self.enable_auto_faker = enable_auto_faker

        self.generators: dict[Any, Callable[..., Any]] = {
            int: self._gen_int,
            float: self._gen_float,
            str: self._gen_str,
            bool: self._gen_bool,
            uuid.UUID: self._gen_uuid,
            datetime: self._gen_datetime,
            date: self._gen_date,
            time: self._gen_time,
            Enum: self._gen_enum,
            Literal: self._gen_literal,
        }
        if extra_generators:
            self.generators.update(extra_generators)

        # simple keyword→faker mapping
        self._auto_faker_map = {
            "email": "email",
            "name": "name",
            "first_name": "first_name",
            "last_name": "last_name",
            "username": "user_name",
            "city": "city",
            "country": "country",
            "phone": "phone_number",
            "address": "address",
            "company": "company",
            "title": "job",
            "zip": "postcode",
            "postal": "postcode",
            "url": "url",
            "uuid": "uuid4",
        }

        if extra_faker_map:
            self._auto_faker_map.update(extra_faker_map)

    # ------------------------------------------------------------------
    def blend(self, model_cls: type[BM], **overrides) -> BM:
        if not issubclass_safe(model_cls, BaseModel):
            raise TypeError(f"Expected Pydantic BaseModel, got {model_cls!r}")

        data = {}
        for name, field in model_cls.model_fields.items():
            key = field.alias or name
            if key in overrides:
                data[key] = overrides[key]
                continue

            annotation = field.annotation
            if get_origin(annotation) in (Union, UnionType):
                args = [t for t in get_args(annotation) if t is not None]
                annotation = args[0] if args else Any
                field.annotation = annotation # type: ignore

            data[key] = self._gen_field(field, key)

        return model_cls(**data)
    
    # ------------------------------------------------------------------
    def blend_many(self, model_cls: type[BM], count: int, **overrides) -> list[BM]:
        return [self.blend(model_cls, **overrides) for _ in range(count)]
    
    def blend_multiple(self, model_cls: Sequence[type[BM]], count: int, **overrides) -> list[BM]:
        return [self.blend(random.choice(model_cls), **overrides) for _ in range(count)]

    # ------------------------------------------------------------------
    def _gen_field(self, field: FieldInfo, field_name: str) -> Any:
        ann = field.annotation
        origin = get_origin(ann)

        # Annotated[str, FakerField(...)]
        if origin is Annotated:
            base, *meta = get_args(ann)
            fk = next((m for m in meta if isinstance(m, FakerField)), None)
            if fk:
                return fk.generate()
            return self.gen_by_type(base)

        # Auto-faker by field name (if enabled)
        if self.enable_auto_faker and _faker and field_name:
            fk_method = self._match_faker_method(field_name)
            if fk_method:
                return getattr(_faker, fk_method)()

        # Union handling
        if origin is Union:
            args = [t for t in get_args(ann) if t is not type(None)]
            ann = args[0] if args else Any

        return self.gen_by_type(ann)

    # ------------------------------------------------------------------
    def _match_faker_method(self, field_name: str) -> str | None:
        """Return faker method name if field name matches mapping."""
        key = field_name.lower()
        for k, method in self._auto_faker_map.items():
            if k in key:
                return method
        return None

    # ------------------------------------------------------------------
    def gen_by_type(self, tp: type[T] | Any) -> T | Any:
        """
        Generate data based on the provided type.

        Args:
            tp (type[T] | Any): The type to generate data for.

        Returns:
            T | Any: The generated data.
        """
        if issubclass_safe(tp, Enum):
            return self._gen_enum(tp)
        if tp in self.generators:
            return self.generators[tp](tp)

        origin = get_origin(tp)
        if origin in self.generators:
            return self.generators[origin](tp)

        if origin in (list, List):
            inner = get_args(tp)[0]
            return [self.gen_by_type(inner) for _ in range(random.randint(1, 4))]

        if issubclass_safe(tp, BaseModel):
            return self.blend(cast(type[BaseModel], tp))
        return None

    # --- Built-in generators -------------------------------------------
    @staticmethod
    def _gen_literal(tp): return random.choice(get_args(tp)) if get_args(tp) else None
    @staticmethod
    def _gen_enum(tp): return random.choice(list(tp)) if list(tp) else None
    @staticmethod
    def _gen_int(_): return random.randint(0, 100_000_000)
    @staticmethod
    def _gen_float(_): return round(random.uniform(0, 1000), 2)
    @staticmethod
    def _gen_str(_): return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    @staticmethod
    def _gen_bool(_): return random.choice([True, False])
    @staticmethod
    def _gen_uuid(_): return uuid.uuid4()
    @staticmethod
    def _gen_datetime(_): return datetime.now()
    @staticmethod
    def _gen_date(_): return date.today()
    @staticmethod
    def _gen_time(_): now = datetime.now(); return time(now.hour, now.minute, now.second)

    # --- Extensibility -------------------------------------------------
    def register(self, tp: Any, generator: Callable[..., Any]) -> None:
        """
        Register your own generator for a specific type.

        Args:
            tp (Any): The type to register the generator for.
            generator (Callable[..., Any]): The generator function.
        """
        self.generators[tp] = generator
