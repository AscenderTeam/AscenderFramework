from typing import Any, get_args
from ascender.schematics.utilities.case_filters import snake_case


def stripped(entity_name: str):
    entity_name = entity_name.removesuffix("Entity")

    return snake_case(entity_name)

def entity_field_type(annotated: type[Any]):
    args = get_args(annotated)
    
    if not args:
        return annotated.__name__
    
    return args[0].__name__