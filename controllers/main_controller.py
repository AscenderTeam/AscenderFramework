from ascender.core.utils.controller import Controller, Get, Post, Delete, Patch


@Controller(
    standalone=True,
    guards=[],
    imports=[],
    providers=[]
)
class MainController:
    def __init__(self):
        ...
    
    @Get()
    async def main_endpoint(self) -> str:
        return "main works!"