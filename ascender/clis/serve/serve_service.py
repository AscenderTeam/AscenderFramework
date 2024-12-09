import os
from fastapi import FastAPI
from ascender.common import Injectable
from ascender.contrib.services import Service
from ascender.core.cli.application import ContextApplication


@Injectable()
class ServeService(Service):
    def __init__(self):
        ...
    
    def start_server(self, app: FastAPI, host: str, port: int):
        import uvicorn
        uvicorn.run("start:app", host=host, port=port, reload=True)