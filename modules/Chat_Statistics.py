import time


class Chat_Statistics:
    Count_Generated = 0
    Count_GeneratedUsed = 0
    Count_GeneratedUsed_RightFirstTime = 0
    Count_Word = 0
    Count_Reply = 0
    Sum_TimeSpend = 0.0
    TS_Last = 0.0
    TS_Use = 0.0

    LastData = {}

    def TimerStart(self):
        self.TS_Last = time.time()

    def TimerEnd(self, Reply: str):
        self.Count_Generated += 1
        TS_Use = time.time() - self.TS_Last
        self.Count_Reply += 1
        self.Sum_TimeSpend += TS_Use
        length = len(Reply)
        if length == 0:
            length = 1
        self.Count_Word += length
        self.LastData = {
            "this": {
                "use": round(TS_Use, 2),
                "SecPerWord": round(TS_Use / length, 2),
            }
        }
        return self.LastData

    def AllData(self):
        return {
            "总计": {
                "模型输出总字数(个)": self.Count_Word,
                "模型生成次数(次)": self.Count_Reply,
                "GPU工作时间(秒)": round(self.Sum_TimeSpend, 3)
            },
            "效率": {
                "平均每字生成时间(秒)": round(self.Sum_TimeSpend / self.Count_Word, 3),
                "平均每次生成时间(秒)": round(self.Sum_TimeSpend / self.Count_Reply, 3),
                "平均每次生成字数(字)": round(self.Count_Word / self.Count_Reply, 3),
            },
            "生成命中率": {
                "完美生成数": self.Count_GeneratedUsed_RightFirstTime
                # "召回概率(%)": round(self.Count_Recall / self.Count_Generated * 100, 3),
                # "生成合格率(%)": round(1 - (self.Count_Recall / self.Count_Generated)*100, 3)
            }
        }
