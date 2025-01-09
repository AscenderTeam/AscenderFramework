from ascender.core import Controller, Get


@Controller(
    standalone=True,
    guards=[],
    imports=[],
    providers=[],
)
class MainController:
    def __init__(self): ...
    
    @Get()
    async def main_endpoint(self) -> str:
        return "main works!"