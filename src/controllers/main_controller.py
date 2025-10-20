from ascender.core import Controller, Get


@Controller(
    standalone=True,
    guards=[],
    imports=[],
    providers=[],
)
class MainController:
    """
    Main controller example.
    
    For dependency injection example:
    
    from services.my_service import MyService
    
    @Controller(standalone=True, providers=[MyService])
    class MainController:
        def __init__(self, my_service: MyService):
            self.my_service = my_service
        
        @Get()
        async def main_endpoint(self):
            return self.my_service.get_data()
    """

    def __init__(self): ...

    @Get()
    async def main_endpoint(self):
        return "main works!"