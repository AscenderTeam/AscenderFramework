from pydantic import BaseModel


class RoleRequirement(BaseModel):
    roles: list[str]
    error_code: int = 403

    def __iter__(self):
        return iter(self.roles)
    
    def __getitem__(self, item: int):
        return self.roles[item]