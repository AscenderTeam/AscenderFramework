from core.database.dbcontext import AppDBContext
from core.extensions.repositories import Repository


class AppRepo(Repository):
    def __init__(self, _context: AppDBContext | None = None) -> None:
        super().__init__(_context)