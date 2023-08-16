import copy


class Model_State:
    out = {}
    model_state = None
    model_tokens = []

    def __init__(self, out, model_tokens, model_state):
        self.out = out
        self.model_tokens = model_tokens
        self.model_state = model_state

    def Out(self):
        return copy.deepcopy(self.out), copy.deepcopy(self.model_tokens), copy.deepcopy(self.model_state)

    def Copy(self):
        return Model_State(copy.deepcopy(self.out), copy.deepcopy(self.model_tokens), copy.deepcopy(self.model_state))

    def Dict(self):
        return {
            "out": self.out,
            "tokens": self.model_tokens,
            "state": self.model_state
        }

    def DebugDict(self, pipeline):
        return {
            "tokens_decoded": pipeline.decode(self.model_tokens),
            "token_count": len(self.model_tokens)
        }


from pydantic import BaseModel


class Model_State_Pydantic(BaseModel):
    out = {}
    model_state = []
    model_tokens = []

    def Dict(self):
        return {
            "out": self.out,
            "tokens": self.model_tokens,
            "state": self.model_state
        }

    def Model_State(self):
        return Model_State(self.out, self.model_tokens, self.model_state)
