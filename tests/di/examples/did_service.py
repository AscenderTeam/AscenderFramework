from ascender.common import Injectable
from ascender.core.applications.application import Application
from ascender.core.services import Service


@Injectable()
class DidService(Service):
    application: Application

    def __init__(self, application: Application):
        self.application = application
