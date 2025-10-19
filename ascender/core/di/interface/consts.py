RAISE_NOT_FOUND = "raise_not_found"

CIRCULAR = object()
NOT_YET = object()

class CyclicDependency(Exception):
    ...