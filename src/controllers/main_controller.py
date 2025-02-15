from ascender.common.base.dto import BaseDTO
from ascender.core import Controller, Get


class PleasureDTO(BaseDTO):
    pleasure_level: int


@Controller(
    standalone=True,
    guards=[],
    imports=[],
    providers=[],
)
class MainController:
    def __init__(self):
        ...
    
    @Get()
    async def main_endpoint(self):
        return "main works!"