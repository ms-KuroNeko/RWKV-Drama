from pydantic import BaseModel

import uuid


class Chat_Line():
    UUID: str = ""
    InputTag: str = ""
    Message: str = ""
    Character: str = ""

    def __init__(self, InputTag: str, Message: str, Character: str = ""):
        self.UUID = str(uuid.uuid1())
        self.InputTag = InputTag
        self.Message = Message
        self.Character = Character

    def Dict(self) -> dict:
        Rtn = {
            "UUID": self.UUID,
            "InputTag": self.InputTag,
            "Message": self.Message,
            "Character": self.Character
        }
        return Rtn

    def __str__(self) -> str:
        if self.InputTag == "系统提示":
            return ""
        elif self.Character:
            return f"{self.Character}:{self.Message}\n\n"
        else:
            return f"{self.Message}\n\n"


# 模板 = {
#     "InputTag": "系统自动|用户输入|模型生成",
#     "Message": "内容",
#     "Character": "此消息的角色，留空为旁白",
#     "Timestamp": "时间"
# }


class Chat_Line_Pydantic(BaseModel):
    InputTag: str = ""
    Message: str = ""
    Character: str = ""

    def Out(self) -> Chat_Line:
        return Chat_Line(self.InputTag, self.Message, self.Character)

    def Dict(self) -> dict:
        return {
            "InputTag": self.InputTag,
            "Message": self.Message,
            "Character": self.Character
        }

    def __str__(self) -> str:
        if self.InputTag == "系统提示":
            return ""
        elif self.Character:
            return f"{self.Character}:{self.Message}\n\n"
        else:
            return f"{self.Message}\n\n"
