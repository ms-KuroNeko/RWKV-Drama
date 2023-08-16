import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default="57860")
parser.add_argument("--model", type=str)
parser.add_argument("--strategy", type=str, default="cuda fp16i8")
parser.add_argument("--listen", action='store_true',
                    help="launch gradio with 0.0.0.0 as server name, allowing to respond to network requests")
parser.add_argument("--cuda_on", type=str, default="0")
parser.add_argument("--jit_on", type=str, default="1")
parser.add_argument("--lang", type=str, default="zh",
                    help="zh: Chinese; en: English")
cmd_opts = parser.parse_args()

import os

os.environ["RWKV_JIT_ON"] = cmd_opts.jit_on
os.environ["RWKV_CUDA_ON"] = cmd_opts.cuda_on
import numpy as np

np.set_printoptions(precision=4, suppress=True, linewidth=200)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from modules.Chat_Line import Chat_Line_Pydantic
from modules.Chat_Scenario import Chat_Scenario
from modules.Chat_Saved import Chat_Saved_Pydantic

from modules.model_utils import ModelUtils
from modules.chat import Chat
from modules.Generate_Config import Generate_Config
from modules.Generate_Request import Generate_Request

# if __name__ == "__main__":
Mdl = ModelUtils(cmd_opts)
Mdl.load_model()

ThisChat = Chat(Mdl)

FstAPI = FastAPI()
FstAPI.mount("/Tester", StaticFiles(directory="Tester"), name="Tester")
FstAPI.mount("/Save", StaticFiles(directory="Save"), name="Save")


@FstAPI.get('/')
def hello():
    return {
        "CatBox":{
            "Type":"RWKV"
        }
    }


@FstAPI.get('/API/Refresh')
def Refresh():
    return {
        "Code": 200, "Msg": "操作成功喵",
        "Data": {
            "ScenarioSeries":ThisChat.CurrentChat_Scenario.ScenarioSeries,
            "ScenarioName":ThisChat.CurrentChat_Scenario.ScenarioName,
            "Characters": ThisChat.CurrentChat_Scenario.CharacterData,
            "History": ThisChat.Lines_History,
            "Pending": ThisChat.Lines_Pending
        }
    }


@FstAPI.get('/API/SysStat')
def DeBug():
    return {"Code": 200, "Msg": "尝试输出所有数据", "Data": ThisChat.SysStat()}

@FstAPI.get('/API/DeBug')
def DeBug():
    return {"Code": 200, "Msg": "尝试输出所有数据", "Data": ThisChat.DebugData()}


@FstAPI.get('/API/Config')
def Config(top_p=-1, top_k=-1, temperature=-1,
           presence_penalty=-1, frequency_penalty=-1,
           max_token=-1):
    if top_p != -1:
        ThisChat.Generate_Config.top_p = top_p
    if top_k != -1:
        ThisChat.Generate_Config.top_k = top_k
    if temperature != -1:
        ThisChat.Generate_Config.temperature = temperature
    if presence_penalty != -1:
        ThisChat.Generate_Config.presence_penalty = presence_penalty
    if frequency_penalty != -1:
        ThisChat.Generate_Config.frequency_penalty = frequency_penalty
    if max_token != -1:
        ThisChat.Generate_Config.max_token = max_token
    return {"Code": 200, "Msg": "操作成功喵", "Data": ThisChat.Generate_Config}


@FstAPI.post('/API/NewChat')
def NewChat(NewChatPrompt: Chat_Scenario):
    ThisChat.Clear()
    print(NewChatPrompt.Prompt)
    return {"Code": 200, "Msg": "操作成功喵", "Data": ThisChat.NewChat(NewChatPrompt)}


@FstAPI.post('/API/LoadChat')
def LoadChat(SavedChat: Chat_Saved_Pydantic):
    ThisChat.Clear()
    print(SavedChat.Scenario.Prompt)
    ThisChat.LoadChat(SavedChat)
    return {"Code": 200, "Msg": "操作成功喵"}


@FstAPI.post('/API/NewMessage')
def NewMessage(NewLine: Chat_Line_Pydantic):
    return {"Code": 200, "Msg": "操作成功喵",
            "Data": ThisChat.NewMessage(NewLine.Out())}


@FstAPI.post('/API/StartGenerate')
def StartGenerate(GR: Generate_Request):
    return {"Code": 200, "Msg": "操作成功喵", "Data": ThisChat.StartGenerate(GR)}


@FstAPI.post('/API/GenerateAgain')
def GenerateAgain():
    return {"Code": 200, "Msg": "操作成功喵", "Data": ThisChat.GenerateAgain()}


@FstAPI.get('/API/SaveAndContinue')
def SaveAndContinue():
    return {"Code": 200, "Msg": "操作成功喵", "Data": ThisChat.SaveAndContinue()}


@FstAPI.get('/API/NGBackAgain')
def BackAgain():
    return {"Code": 200, "Msg": "操作成功喵", "Data": ThisChat.NGBackAgain()}


@FstAPI.get('/API/UndoLine')
def UndoLine():
    return {"Code": 200, "Msg": "操作成功喵", "Data": ThisChat.UndoLine()}


@FstAPI.get('/API/SaveCheckPoint')
def SaveCheckPoint(CheckName):
    return {"Code": 200, "Msg": "操作成功喵", "Data": ThisChat.SaveCheckPoint(CheckName)}


@FstAPI.get('/API/SaveToLog')
def SaveToLog():
    return {"Code": 200, "Msg": "操作成功喵", "Data": ThisChat.Saver.SaveLog()}


# 集群系统控制

@FstAPI.get('/API/CheckSynchronized')
def CheckSynchronized(PipelineTokenMD5):
    return {"Code": 200, "Msg": "操作成功喵", "Data": ThisChat.Synchronizer.CheckSynchronized()}


@FstAPI.get('/API/CurrentToken')
def CurrentToken():
    return {
        "Code": 200, "Msg": "操作成功喵",
        "Data": {
            "Scenario": ThisChat.CurrentChat_Scenario,
            "Chat": ThisChat.Lines_History
        }
    }

@FstAPI.get("/items/", response_class=HTMLResponse)
def read_items():
    return """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """


import uvicorn

uvicorn.run(FstAPI, host="0.0.0.0", port=cmd_opts.port)
