class AscenderConfigError(Exception):
    def __init__(self, codename: str, message: str | None = None):
        self.codename = codename
        self.message = message or "An error occurred in the Ascender configuration."
        super().__init__(f"[{self.codename}] {self.message}")