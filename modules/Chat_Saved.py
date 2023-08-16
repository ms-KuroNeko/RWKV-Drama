from pydantic import BaseModel

from modules.Chat_Line import Chat_Line_Pydantic
from modules.Chat_Scenario import Chat_Scenario


class Chat_Saved_Pydantic(BaseModel):
    Scenario: Chat_Scenario
    Chat: list[Chat_Line_Pydantic]

