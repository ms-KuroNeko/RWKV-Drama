import json
import os
from datetime import datetime

from modules import chat


class Saver:
    BindChat: chat

    def __init__(self, Chat: chat):
        self.BindChat = Chat
        self.DateTime = datetime.now().strftime("%Y%m%d-%H%M")

    def SaveDir(self):
        return f'./Save/{self.BindChat.CurrentChat_Scenario.ScenarioSeries}/{self.BindChat.CurrentChat_Scenario.ScenarioName}'

    def SaveScenario(self):
        os.makedirs(self.SaveDir(), exist_ok=True)
        ScenarioFileName = f'{self.SaveDir()}/场景剧本.json'
        with open(ScenarioFileName, 'w', encoding='utf-8') as f:
            json.dump(self.BindChat.CurrentChat_Scenario.Dict(), f,
                      ensure_ascii=False, indent=2, default=lambda cl: cl.Dict())

    def SaveLog(self):
        LogFileName = f'{self.SaveDir()}/{self.DateTime}_Log.json'
        with open(LogFileName, 'w', encoding='utf-8') as f:
            json.dump({
                "Scenario": self.BindChat.CurrentChat_Scenario,
                "Chat": self.BindChat.Lines_History
            }, f, ensure_ascii=False, indent=2, default=lambda cl: cl.Dict())
