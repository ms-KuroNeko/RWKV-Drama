from modules.model_utils import ModelUtils
import pickle
import copy
import re
import gc
import torch

from modules.Generate_Config import Generate_Config
from modules.Model_State import Model_State
import uuid

from modules.Chat_Statistics import Chat_Statistics
from modules.Chat_Line import Chat_Line
from modules.Chat_Scenario import Chat_Scenario
from modules.Chat_Saved import Chat_Saved_Pydantic
from modules.Generate_Request import Generate_Request
from modules.Saver import Saver


class Chat:
    CurrentChat_Scenario: Chat_Scenario

    ModelState_Init: Model_State
    ModelState_Confirmed: Model_State
    ModelState_Pending: Model_State

    Lines_History: list[Chat_Line] = []
    Lines_Pending: list[Chat_Line] = []
    PendingStepText: str = ""

    model_utils = None

    Statistics: Chat_Statistics

    Saver = None

    LastGR: Generate_Request

    def __init__(self, model_utils: ModelUtils):
        self.model_utils = model_utils
        self.Statistics = Chat_Statistics()
        print("正在初始化Chat")

    def NewChat(self, NewChat_Scenario: Chat_Scenario):
        self.Clear()
        self.CurrentChat_Scenario = NewChat_Scenario
        self.ModelState_Init = self.model_utils.run_rnn(
            Model_State(None, [], None), self.model_utils.pipeline.encode(str(self.CurrentChat_Scenario)))
        self.Lines_History.append(Chat_Line("系统提示", "已载入角色卡，正在构建对话", "系统提示"))
        Sliced = self.CurrentChat_Scenario.Example.split('\n\n')
        for line in Sliced:
            if len(line.strip()) > 2:
                LineSliced = line.split(': ')
                if len(LineSliced) == 2:
                    self.Lines_History.append(
                        Chat_Line("初始对话", LineSliced[1].strip(), LineSliced[0].strip()))
                else:
                    self.Lines_History.append(
                        Chat_Line("初始对话", LineSliced[0].strip(), ""))

        self.ModelState_Confirmed = self.ModelState_Init.Copy()
        self.ModelState_Pending = self.ModelState_Init.Copy()
        self.Lines_History.append(Chat_Line("系统提示", "已载入前置对话", "系统提示"))
        self.Saver.SaveScenario()
        return NewChat_Scenario

    def LoadChat(self, OldChat: Chat_Saved_Pydantic):
        self.Clear()
        self.CurrentChat_Scenario = OldChat.Scenario
        self.ModelState_Init = self.model_utils.run_rnn(
            Model_State(None, [], None), self.model_utils.pipeline.encode(str(self.CurrentChat_Scenario.Prompt)))
        self.ModelState_Confirmed = self.ModelState_Init.Copy()
        self.ModelState_Pending = self.ModelState_Init.Copy()
        self.Lines_History = []
        self.Lines_Pending = OldChat.Chat
        self.__RemakePendingStepText__()
        self.SaveAndContinue()
        self.Lines_History.append(Chat_Line("系统提示", "已载入历史对话", "系统提示"))
        return True

    def Clear(self):
        print("正在重置Chat")
        self.UUID: str = str(uuid.uuid1())
        self.Statistics = Chat_Statistics()
        self.Lines_History = []
        self.Lines_Pending = []
        self.PendingStepText = ""
        self.ModelState_Init = None
        self.ModelState_Confirmed = None
        self.ModelState_Pending = None
        self.CurrentChat_Scenario = None
        self.LastGR = None
        self.Saver = Saver(self)


    def NewMessage(self, NewLine: Chat_Line):
        # ModelState = self.model_utils.run_rnn(self.ModelState_Confirmed,
        #                                       self.model_utils.pipeline.encode(str(NewLine)))
        # self.ModelState_Confirmed = ModelState
        # NewLine.ModelState = ModelState
        self.PendingStepText += str(NewLine)
        self.Lines_Pending.append(NewLine)
        if (NewLine.InputTag.startswith("模型生成")):
            self.Statistics.Count_GeneratedUsed + 1
            if (NewLine.InputTag == "模型生成"):
                self.Statistics.Count_GeneratedUsed_RightFirstTime
        return {
            "Lines_Pending": self.Lines_Pending
        }

    def StartGenerate(self, GR: Generate_Request):
        if GR.Character == "":
            GR.Character = self.CurrentChat_Scenario.CharacterData["AI"][0]
        self.LastGR = GR
        self.__RemakePendingStepText__()
        self.PendingStepText += str(GR)
        self.ModelState_Pending = self.model_utils.run_rnn(
            self.ModelState_Confirmed, self.model_utils.pipeline.encode(self.PendingStepText))
        return {
            "Lines_Pending": self.Lines_Pending,
            "Reply": self.__Generate__(self.LastGR),
            "Request": self.LastGR
        }

    def GenerateAgain(self):
        return {
            "Lines_Pending": self.Lines_Pending,
            "Reply": self.__Generate__(self.LastGR),
            "Request": self.LastGR
        }

    def __Generate__(self, GR):
        self.Statistics.TimerStart()
        out, model_tokens, model_state = self.ModelState_Pending.Out()
        new_reply = ""
        while new_reply.strip() == "" or ": " in new_reply:
            reply, out, model_tokens, model_state, = self.model_utils.get_reply(
                model_tokens, model_state, out, GR.Cfg)
            new_reply = reply.strip()
        self.Statistics.TimerEnd(new_reply)
        return new_reply

    def SaveAndContinue(self):
        self.__RemakePendingStepText__()
        self.ModelState_Confirmed = self.model_utils.run_rnn(
            self.ModelState_Confirmed,
            self.model_utils.pipeline.encode(str(self.PendingStepText)))
        self.ModelState_Pending = self.ModelState_Confirmed.Copy()
        self.Lines_History += self.Lines_Pending
        self.Lines_Pending = []
        self.PendingStepText = ""

    def UndoLine(self):
        self.Lines_Pending.pop()
        return {
            "Lines_Pending": self.Lines_Pending
        }

    def __RemakePendingStepText__(self):
        self.PendingStepText = ""
        for line in self.Lines_Pending:
            self.PendingStepText += str(line)

    def NGBackAgain(self):
        self.ModelState_Pending = self.ModelState_Confirmed.Copy()
        self.Lines_Pending = []
        self.PendingStepText = ""

    def SaveCheckPoint(self, CPName):
        self.Lines_History[-1].ModelState = 1
        self.ModelState_Confirmed[CPName] = {
            "LineUUID": self.Lines_History[-1].UUID,
            "Model": self.ModelState_Confirmed.Copy()
        }

    def AllData(self):
        Rtn = {
            "CurrentChat_Scenario": self.CurrentChat_Scenario.Dict(),
            "Chat": {
                "History": {
                    "Lines_History": self.Lines_History,
                    "Lines_Pending": self.Lines_Pending
                },
                "Pending": {
                    "StepText": self.PendingStepText
                }
            },
            "Model": {
                "Main": {},
                "Init": {},
                "Pending": {}
            }
        }
        try:
            Rtn["Model"]["Main"] = self.ModelState_Confirmed.DebugDict(
                self.model_utils.pipeline)
            Rtn["Model"]["Init"] = self.ModelState_Init.DebugDict(
                self.model_utils.pipeline)
            Rtn["Model"]["Pending"] = self.ModelState_Confirmed.DebugDict(
                self.model_utils.pipeline)
            Rtn["Pending"]["ModelDecode"] = self.ModelState_Pending.DebugDict(
                self.model_utils.pipeline)
            # for (id, ms) in self.ModelState_Confirmed:
            #     Rtn["Model"]["Saved"][id] = ms.DebugDict(
            #         self.model_utils.pipeline)
        except:
            print("AllDataError")
        return Rtn

    def SysStat(self):
        Rtn = {
            "Statistics": self.Statistics.AllData(),
            "TokenLength": len(self.ModelState_Pending.model_tokens)
        }
        return Rtn
    
    def DebugData(self):
        Rtn = {
            "Pending": {
                "Lines_Pending": self.Lines_Pending,
                "StepText": self.PendingStepText
            },
            "Model": {
                "Main": {},
                "Init": {},
                "Pending": {}
            }
        }
        try:
            Rtn["Model"]["Main"] = self.ModelState_Confirmed.DebugDict(
                self.model_utils.pipeline)
            Rtn["Model"]["Init"] = self.ModelState_Init.DebugDict(
                self.model_utils.pipeline)
            Rtn["Model"]["Pending"] = self.ModelState_Confirmed.DebugDict(
                self.model_utils.pipeline)
            Rtn["Pending"]["ModelDecode"] = self.ModelState_Pending.DebugDict(
                self.model_utils.pipeline)
            # for (id, ms) in self.ModelState_Confirmed:
            #     Rtn["Model"]["Saved"][id] = ms.DebugDict(
            #         self.model_utils.pipeline)
        except:
            print("AllDataError")
        return Rtn

    def Check_TokenCount(self) -> bool:
        return len(self.ModelState_Confirmed.model_tokens) > self.LastGR.Cfg.max_token

    def SaveAll(self):
        Rtn = {
            "CurrentChat_Scenario": self.CurrentChat_Scenario,
            "Lines": {
                "Lines_History": self.Lines_History,
                "Lines_Pending": self.Lines_Pending
            }
        }
        try:
            Rtn["Model"] = self.ModelState_Confirmed
        except:
            print("AllDataError")
        return Rtn
