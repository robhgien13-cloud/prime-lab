"""Offline, reproducible cross-domain inspiration picker for PRIME LAB."""
import hashlib
import random

WORDS = {
    "自然": ["潮汐","樹木","菌類","渡り鳥","雪崩","珊瑚","砂丘","年輪","霧","渦"],
    "社会": ["市場","都市","選挙","交通網","移住","言語","貨幣","法律","協力","競争"],
    "芸術": ["旋律","彫刻","舞踊","遠近法","色彩","詩","和音","映画","建築","模様"],
    "科学": ["磁場","結晶","重力","軌道","波動","遺伝","触媒","熱","量子","振動"],
    "日常": ["鍵","階段","傘","時計","料理","窓","靴","橋","迷路","鏡"],
    "技術": ["暗号","圧縮","通信","センサー","ロボット","回路","記憶","検索","誤り訂正","信号"],
}
def pick(day, count=3):
    """Same UTC date produces the same distinct-domain words."""
    if not isinstance(day,str) or len(day)!=10: raise ValueError("Expected ISO date")
    if type(count) is not int or not 1<=count<=len(WORDS): raise ValueError("Invalid count")
    seed=int.from_bytes(hashlib.sha256(day.encode("utf-8")).digest(),"big")
    rng=random.Random(seed)
    domains=rng.sample(sorted(WORDS),count)
    return [{"domain":d,"word":rng.choice(WORDS[d])} for d in domains]
