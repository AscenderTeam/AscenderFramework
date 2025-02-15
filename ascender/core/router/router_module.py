from typing import Sequence, TYPE_CHECKING

from ascender.core.router.interface.route import RouterRoute

if TYPE_CHECKING:
    from ascender.core import Provider


def routerForChildren(routes: Sequence[RouterRoute]) -> "Provider":
    return {
        "provide": "ROUTER_MODULE",
        "value": routes
    }