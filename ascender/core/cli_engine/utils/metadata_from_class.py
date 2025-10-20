from __future__ import annotations

import inspect
from typing import Any, Dict, Mapping, Sequence, get_args, get_origin, ClassVar
from typing_extensions import Annotated, Doc

from ascender.core.cli_engine.types.parameter import ParameterInfo


def _inspect_annotated(tp: Any) -> tuple[Any, Sequence[Any]]:
    """
    For Annotated[T, ...] return (T, metadata_seq),
    otherwise (tp, ()).
    """
    if get_origin(tp) is Annotated:
        base, *meta = get_args(tp)
        return base, meta
    # fallback for older typing behavior that exposes __metadata__
    meta = getattr(tp, "__metadata__", None)
    if meta is not None:
        args = get_args(tp)
        base = args[0] if args else tp
        return base, meta
    return tp, ()


def _pick_paraminfo_and_doc(meta: Sequence[Any]) -> tuple[ParameterInfo | None, str | None]:
    pi = None
    help_txt = None
    for m in meta:
        if isinstance(m, ParameterInfo):
            pi = m
        elif isinstance(m, Doc) and help_txt is None:
            help_txt = m.documentation
    return pi, help_txt


# ---------- CLASS ANALOGS ----------

def _annotations_from_class(cls: type) -> Dict[str, Any]:
    """
    Collects field annotations across MRO (base -> subclass), excluding ClassVar.
    Subclass entries override base ones.
    """
    out: Dict[str, Any] = {}
    for base in reversed(cls.__mro__):
        if base is object:
            continue
        ann = getattr(base, "__annotations__", {}) or {}
        for name, tp in ann.items():
            if get_origin(tp) is ClassVar:
                continue
            out[name] = tp
    return out


def _get_class_parameters(cls: type) -> Mapping[str, ParameterInfo]:
    """
    Build ParameterInfo map from a BasicCLI-style class.
    - Use class annotations as the schema.
    - Use class attribute values as defaults.
    - If Annotated[..., ParameterInfo] present, that wins.
    - Else, Annotated[..., Doc(...)] provides help.
    - Required if no default provided anywhere.
    """
    param_infos: dict[str, ParameterInfo] = {}
    ann_map = _annotations_from_class(cls)

    for name, annotation in ann_map.items():
        # skip methods / descriptors accidentally annotated
        attr = getattr(cls, name, inspect._empty)
        if callable(attr) or isinstance(attr, (staticmethod, classmethod)):
            continue

        base_type, meta = _inspect_annotated(annotation)
        pinfo_meta, doc_help = _pick_paraminfo_and_doc(meta)

        # choose or create ParameterInfo
        if isinstance(attr, ParameterInfo):
            pi = attr
        elif pinfo_meta is not None:
            pi = pinfo_meta
        else:
            pi = ParameterInfo(name, dest=name)

        # annotation
        pi.annotation = base_type

        # default: explicit ParameterInfo.default wins; otherwise class attr value if not empty
        if getattr(pi, "default", ...) is ... and attr is not inspect._empty and not isinstance(attr, (staticmethod, classmethod)):
            pi.default = attr

        # help: Doc(...) only if ParameterInfo.help not set
        if doc_help and not getattr(pi, "help", None):
            pi.help = doc_help

        # required if no default set anywhere
        required = getattr(pi, "default", ...) is ...

        # if optional and no custom flag names, synthesize --kebab-case
        if not required and not pi.name_or_flags:
            pi.name_or_flags = [f"--{name.replace('_', '-')}"]

        param_infos[name] = pi

    return param_infos