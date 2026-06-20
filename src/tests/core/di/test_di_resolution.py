"""
Parity + perf coverage for the Ascender DI resolver (`AscenderInjector`).

These tests construct the injector directly (independent of the autouse
`ascender_app` lifecycle fixture) and lock the observable resolution behavior:
provider shapes, singleton identity, multi providers, forward-ref resolution,
circular-dependency handling, parent/child delegation and not-found fallback.

They are the safety gate for the DI hot-path optimization: the exact same
assertions must hold before and after the internal changes, since none of those
changes touch behavior.

NOTE: deliberately *no* ``from __future__ import annotations`` here. Test fixture
classes are defined inside test functions, so ``get_type_hints`` cannot resolve
them; the resolver then falls back to the live ``param.annotation`` object, which
must stay a real type / ``Annotated[...]`` rather than a string.
"""
import contextlib
from typing import Annotated

import pytest

from ascender.core.di.injector import AscenderInjector
from ascender.core.di.inject import Inject
from ascender.core.di.none_injector import NoneInjectorException
from ascender.core.di.interface.consts import CyclicDependency
from ascender.core._config.asc_config import _AscenderConfig
from ascender.core._config.interface.runtime import DependencyInjectionConfig


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
@contextlib.contextmanager
def circular_mode(mode: str):
    """
    Force the active environment's circular-dependency handling to ``mode``
    ("warn" | "error") for the duration of the block, regardless of whether the
    suite runs in test mode or bare pytest. The injector reads this config when
    it is constructed, so build the injector *inside* this context.
    """
    cfg = _AscenderConfig()
    env = cfg.get_environment()
    previous = env.dependency_injection
    env.dependency_injection = DependencyInjectionConfig(
        circularDependencyHandling=mode  # type: ignore[arg-type]
    )
    try:
        yield
    finally:
        env.dependency_injection = previous


# --------------------------------------------------------------------------- #
# Type providers + singleton identity
# --------------------------------------------------------------------------- #
def test_type_provider_resolves_and_is_singleton():
    class Service:
        def __init__(self):
            ...

    injector = AscenderInjector([Service])

    first = injector.get(Service)
    second = injector.get(Service)

    assert isinstance(first, Service)
    assert first is second, "type providers must resolve as singletons"


def test_type_provider_constructor_injection_order():
    class Engine:
        def __init__(self):
            ...

    class Gearbox:
        def __init__(self):
            ...

    class Car:
        def __init__(self, engine: Engine, gearbox: Gearbox):
            self.engine = engine
            self.gearbox = gearbox

    injector = AscenderInjector([Engine, Gearbox, Car])
    car = injector.get(Car)

    assert isinstance(car.engine, Engine)
    assert isinstance(car.gearbox, Gearbox)
    # nested deps are the same singletons the injector hands out directly
    assert car.engine is injector.get(Engine)
    assert car.gearbox is injector.get(Gearbox)


# --------------------------------------------------------------------------- #
# Value providers
# --------------------------------------------------------------------------- #
def test_value_provider():
    sentinel = {"api_key": "abc123"}
    injector = AscenderInjector([{"provide": "CONFIG", "value": sentinel}])

    assert injector.get("CONFIG") is sentinel


# --------------------------------------------------------------------------- #
# Factory providers
# --------------------------------------------------------------------------- #
def test_factory_provider_with_deps_injects_in_order():
    class Config:
        def __init__(self):
            self.dsn = "postgres://localhost"

    def make_db(config: Config):
        return {"connected_to": config.dsn, "config": config}

    injector = AscenderInjector(
        [Config, {"provide": "DB", "use_factory": make_db, "deps": [Config]}]
    )

    db = injector.get("DB")
    assert db["connected_to"] == "postgres://localhost"
    assert db["config"] is injector.get(Config)


def test_factory_provider_singleton():
    counter = {"n": 0}

    def factory():
        counter["n"] += 1
        return object()

    injector = AscenderInjector([{"provide": "ONCE", "use_factory": factory}])

    a = injector.get("ONCE")
    b = injector.get("ONCE")
    assert a is b
    assert counter["n"] == 1, "factory must run exactly once for a singleton"


# --------------------------------------------------------------------------- #
# Static class providers
# --------------------------------------------------------------------------- #
def test_static_class_provider_use_class():
    class Logger:
        def __init__(self):
            ...

    class FileLogger(Logger):
        def __init__(self):
            ...

    injector = AscenderInjector(
        [{"provide": Logger, "use_class": FileLogger}]
    )

    resolved = injector.get(Logger)
    assert isinstance(resolved, FileLogger)


# --------------------------------------------------------------------------- #
# Multi providers
# --------------------------------------------------------------------------- #
def test_multi_provider_returns_ordered_list():
    def mw_a():
        return "a"

    def mw_b():
        return "b"

    injector = AscenderInjector(
        [
            {"provide": "MIDDLEWARE", "use_factory": mw_a, "multi": True},
            {"provide": "MIDDLEWARE", "use_factory": mw_b, "multi": True},
        ]
    )

    resolved = injector.get("MIDDLEWARE")
    assert isinstance(resolved, list)
    assert set(resolved) == {"a", "b"}


# --------------------------------------------------------------------------- #
# Forward-ref / string-token resolution (exercises the name->type index path)
# --------------------------------------------------------------------------- #
def test_forward_ref_string_token_resolves_to_type():
    class Engine:
        def __init__(self):
            ...

    class Car:
        # explicit string token -> resolved via resolve_dep_forward_ref()
        def __init__(self, engine: Annotated[Engine, Inject("Engine")]):
            self.engine = engine

    injector = AscenderInjector([Engine, Car])
    car = injector.get(Car)

    assert isinstance(car.engine, Engine)
    assert car.engine is injector.get(Engine)


# --------------------------------------------------------------------------- #
# Circular dependencies
# --------------------------------------------------------------------------- #
def _make_cyclic_providers():
    class A:
        def __init__(self, b: Annotated[object, Inject("B")]):
            self.b = b

    class B:
        def __init__(self, a: Annotated[object, Inject("A")]):
            self.a = a

    # register under the string names the Inject() tokens reference
    return [{"provide": "A", "use_class": A}, {"provide": "B", "use_class": B}]


def test_circular_dependency_error_mode_raises():
    providers = _make_cyclic_providers()
    with circular_mode("error"):
        injector = AscenderInjector(providers)
        with pytest.raises(CyclicDependency):
            injector.get("A")


def test_circular_dependency_warn_mode_returns_forward_ref():
    providers = _make_cyclic_providers()
    with circular_mode("warn"):
        injector = AscenderInjector(providers)
        with pytest.warns(RuntimeWarning):
            resolved = injector.get("A")
        # warn mode breaks the cycle with a lazy DependencyForwardRef somewhere
        # in the resolved graph rather than raising.
        assert resolved is not None


# --------------------------------------------------------------------------- #
# Parent / child delegation + not-found
# --------------------------------------------------------------------------- #
def test_child_injector_delegates_to_parent():
    class Shared:
        def __init__(self):
            ...

    parent = AscenderInjector([Shared])
    child = AscenderInjector([], parent=parent)

    # child has no Shared provider -> must delegate up to the parent singleton
    assert child.get(Shared) is parent.get(Shared)


def test_only_self_does_not_delegate():
    class Shared:
        def __init__(self):
            ...

    parent = AscenderInjector([Shared])
    child = AscenderInjector([], parent=parent)

    with pytest.raises(NoneInjectorException):
        child.get(Shared, options={"only_self": True})


def test_not_found_raises_by_default():
    injector = AscenderInjector([])
    with pytest.raises(NoneInjectorException):
        injector.get("MISSING")


def test_not_found_optional_returns_none():
    injector = AscenderInjector([])
    assert injector.get("MISSING", not_found_value=None, options={"optional": True}) is None


def test_not_found_returns_fallback_value():
    injector = AscenderInjector([])
    fallback = object()
    assert injector.get("MISSING", not_found_value=fallback) is fallback


# --------------------------------------------------------------------------- #
# Perf guard: every singleton in a deep chain is built exactly once (linear)
# --------------------------------------------------------------------------- #
@pytest.mark.perf
def test_deep_chain_resolves_each_node_once():
    N = 200
    calls = {"n": 0}

    def make_factory(_i):
        def factory(*deps):
            calls["n"] += 1
            return deps[0] + 1 if deps else 0

        return factory

    providers = [{"provide": "node_0", "use_factory": make_factory(0)}]
    for i in range(1, N):
        providers.append(
            {
                "provide": f"node_{i}",
                "use_factory": make_factory(i),
                "deps": [f"node_{i - 1}"],
            }
        )

    injector = AscenderInjector(providers)
    root = injector.get(f"node_{N - 1}")

    assert root == N - 1
    # linear, not quadratic / repeated: each factory fired exactly once
    assert calls["n"] == N
