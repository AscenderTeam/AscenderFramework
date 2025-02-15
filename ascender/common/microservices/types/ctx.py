class CtxMetadata:
    context_type: bool = True


def Ctx():
    return CtxMetadata()

__all__ = ["Ctx"]