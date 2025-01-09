from typing import Sequence
from ascender.core.router.interface.route import RouterRoute
from ascender.core import Provider


def routerForChildren(routes: Sequence[RouterRoute]) -> Provider:
    return {
        "provide": "ROUTER_MODULE",
        "value": routes
    }