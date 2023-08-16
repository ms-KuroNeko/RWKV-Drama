from pydantic import BaseModel

from modules.Generate_Config import Generate_Config

class Generate_Request(BaseModel):
    Character: str = ""
    StartWith = ""
    Lines = 1
    MinLength = 0
    Cfg:Generate_Config

    def __str__(self):
        return f"{self.Character}: {self.StartWith}"