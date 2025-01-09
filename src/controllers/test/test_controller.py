from ascender.core import Controller, Get
from ascender.core.struct.routes import Post
from controllers.test.test_service import TestService


@Controller(
    standalone=False,
    guards=[],
)
class TestController:
    def __init__(self, test_service: TestService):
        self.test_service = test_service
    
    @Post()
    async def test_endpoint(self, username: str):
        return await self.test_service.create_user(username)