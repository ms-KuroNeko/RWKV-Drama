from pydantic import BaseModel

class Generate_Config(BaseModel):
    top_p = 0.7
    top_k = 0
    temperature = 2
    presence_penalty = 0.5
    frequency_penalty = 0.5
    max_token = 7788
    turns = 1
    min_len = 0

    def Dict(self):
        return {
            'top_p': self.top_p,
            'top_k': self.top_k,
            'temperature': self.temperature,
            'presence_penalty': self.presence_penalty,
            'frequency_penalty': self.frequency_penalty,
            'max_token': self.max_token,
            'turns': self.turns,
            'min_len': self.min_len
        }
