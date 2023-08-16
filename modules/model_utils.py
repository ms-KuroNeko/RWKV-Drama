from rwkv.utils import PIPELINE
from rwkv.model import RWKV
import copy
import gc
import os
import torch

from modules.Generate_Config import Generate_Config
from modules.Model_State import Model_State

torch.backends.cudnn.benchmark = True
torch.backends.cudnn.allow_tf32 = True
torch.backends.cuda.matmul.allow_tf32 = True


class ModelUtils:
    model = None
    pipline = None
    model_path = None
    strategy = None
    CHUNK_LEN = 100
    END_OF_TEXT = 0
    END_OF_LINE = 11
    DOUBLE_END_OF_LINE = 261
    CHN_PERIOD = 10080
    CHN_PERIOD_END = 28329
    NEG_INF = -999999999
    AVOID_REPEAT = '，：？！'
    AVOID_REPEAT_TOKENS = []
    all_state = {}

    def __init__(self, args) -> None:
        self.model_path = args.model
        self.strategy = args.strategy
        self.model_name = os.path.basename(self.model_path).rstrip('.pth')
        print("正在初始化ModelUtils")

    def load_model(self) -> None:
        self.model = RWKV(model=self.model_path, strategy=self.strategy)
        upper_path = self.model_path.upper()
        if "WORLD" in upper_path:
            self.pipeline = PIPELINE(self.model, "rwkv_vocab_v20230424")
        elif "RAVEN" in upper_path:
            self.pipeline = PIPELINE(self.model, "./rwkv/20B_tokenizer.json")
        for i in self.AVOID_REPEAT:
            dd = self.pipeline.encode(i)
            assert len(dd) == 1
            self.AVOID_REPEAT_TOKENS += dd

    def run_rnn(self, MdlStat: Model_State, tokens: object) -> Model_State:
        out, model_tokens, model_state = MdlStat.Out()
        tokens = [int(x) for x in tokens]
        model_tokens += tokens
        while len(tokens) > 0:
            out, model_state = self.model.forward(
                tokens[:self.CHUNK_LEN], model_state)
            tokens = tokens[self.CHUNK_LEN:]
        if model_tokens[-1] in self.AVOID_REPEAT_TOKENS:
            out[model_tokens[-1]] = self.NEG_INF
        return Model_State(out, model_tokens, model_state)

    def run_rnn_(self, model_tokens, model_state, tokens):
        tokens = [int(x) for x in tokens]
        model_tokens += tokens
        while len(tokens) > 0:
            out, model_state = self.model.forward(
                tokens[:self.CHUNK_LEN], model_state)
            tokens = tokens[self.CHUNK_LEN:]
        if model_tokens[-1] in self.AVOID_REPEAT_TOKENS:
            out[model_tokens[-1]] = self.NEG_INF
        return out, model_tokens, model_state

    def get_reply(self, model_tokens, model_state, out, GenCfg:Generate_Config):
        gc.collect()
        torch.cuda.empty_cache()
        begin = len(model_tokens)
        out_last = begin
        occurrence = {}
        turns=GenCfg.turns
        for i in range(999):
            if GenCfg.min_len> 0 and i < GenCfg.min_len:
                out[self.CHN_PERIOD_END] = self.NEG_INF
                out[self.DOUBLE_END_OF_LINE] = self.NEG_INF
                out[self.END_OF_LINE] = self.NEG_INF
            for n in occurrence:
                out[n] -= (GenCfg.presence_penalty + occurrence[n] * GenCfg.frequency_penalty)
            token = self.pipeline.sample_logits(out, GenCfg.temperature, GenCfg.top_p, GenCfg.top_k)
            if turns > 1:
                if token == self.DOUBLE_END_OF_LINE:
                    out[self.DOUBLE_END_OF_LINE] = self.NEG_INF
                    out[self.END_OF_LINE] = self.NEG_INF
                    turns -= 1
                    continue
                if token == self.CHN_PERIOD_END:
                    token = self.CHN_PERIOD
                    out[self.CHN_PERIOD_END] = self.NEG_INF
                    out[self.DOUBLE_END_OF_LINE] = self.NEG_INF
                    out[self.END_OF_LINE] = self.NEG_INF
                    turns -= 1
            occurrence[token] = 1 + \
                (occurrence[token] if token in occurrence else 0)
            out, model_tokens, model_state = self.run_rnn_(
                model_tokens, model_state, [token])
            out[self.END_OF_TEXT] = self.NEG_INF
            xxx = self.pipeline.decode(model_tokens[out_last:])
            if '\ufffd' not in xxx:  # avoid utf-8 display issues
                out_last = begin + i + 1
            send_msg = self.pipeline.decode(model_tokens[begin:])
            if '\n\n' in send_msg:
                send_msg = send_msg.strip()
                break
        return send_msg, out, model_tokens, model_state

    def format_chat_param(self, top_p, top_k, temperature, presence_penalty, frequency_penalty, turns=1, min_len=0):
        chat_param = {
            'top_p': top_p,
            'top_k': top_k,
            'temperature': temperature,
            'presence_penalty': presence_penalty,
            'frequency_penalty': frequency_penalty,
            'turns': turns,
            'min_len': min_len
        }
        return chat_param
