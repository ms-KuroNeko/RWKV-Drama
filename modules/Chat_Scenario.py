from pydantic import BaseModel

from modules.Chat_Line import Chat_Line


class Chat_Scenario(BaseModel):
    ScenarioSeries: str
    ScenarioName: str
    Prompt: str
    Example: str
    CharacterData: dict

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("警告：重置剧本")

    def __str__(self):
        return f"{self.Prompt}\n\n{self.Example}\n\n"

    def Dict(self):
        Rtn = {
            "ScenarioSeries": self.ScenarioSeries,
            "ScenarioName": self.ScenarioName,
            "Prompt": self.Prompt,
            "Example": self.Example,
            "CharacterData": self.CharacterData
        }
        return Rtn
