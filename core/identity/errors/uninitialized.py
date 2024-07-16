class UninitializedSecurity(Exception):
    def __str__(self) -> str:
        return "Identity Security Module isn't initialized in `bootstrap.py`. Please add `app.add_authorization(...)` in `Bootstrap.server_boot_up()` method"