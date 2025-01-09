from ascender.common import Injectable
from ascender.core import Service
from controllers.test.test_repository import TestRepo


@Injectable()
class TestService(Service):
    def __init__(self, test_repo: TestRepo):
        self.test_repo = test_repo
    
    async def create_user(self, username: str):
        return await self.test_repo.create_user(name=username)