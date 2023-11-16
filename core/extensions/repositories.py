class Repository:
    def __init__(self, **entities) -> None:
        for key, value in entities.items():
            setattr(self, key, value)