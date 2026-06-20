"""
Coverage for the explicit Application boot pipeline (`Application.bootstrap`).

Locks the two properties that matter after moving the startup logic out of the
unguarded `__call__`:
  * `bootstrap()` is idempotent — calling it repeatedly mounts routes only once.
  * `__call__` (the uvicorn `factory=True` entrypoint) is just a thin delegate
    to `bootstrap()` and returns the same FastAPI instance.
"""
from fastapi import FastAPI

from ascender.core.applications.application import Application


def test_bootstrap_is_idempotent(ascender_app: Application):
    app = ascender_app

    first = app.bootstrap()
    routes_after_first = len(app.app.routes)

    second = app.bootstrap()

    assert app._booted is True
    assert first is second is app.app
    assert isinstance(app.app, FastAPI)
    # second boot must not re-mount the route graph
    assert len(app.app.routes) == routes_after_first


def test_call_delegates_to_bootstrap(ascender_app: Application):
    app = ascender_app

    built = app.bootstrap()
    via_call = app()  # uvicorn factory entrypoint

    assert via_call is built is app.app
    assert app._booted is True
