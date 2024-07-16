from threading import Lock
from typing import Self

from core.identity.errors.uninitialized import UninitializedSecurity
from core.identity.security import Security


class SecuritySingleton:
    _instance: Security | None = None
    _lock: Lock = Lock()

    def __new__(cls, instance: Security | None = None) -> Security:
        with cls._lock:
            if not cls._instance:
                if instance is None:
                    raise UninitializedSecurity()
                cls._instance = instance
        
        return cls._instance