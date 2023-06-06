# -*- coding: utf-8 -*-
from pathlib import Path

_m = []
try:
    with Path(__file__).parent.joinpath("statics/phrases.txt").resolve().open("r", encoding='UTF-8') as fin:
        while True:
            l = fin.readline()
            if not l:break
            l = l.strip("\n")
            ll = l.split("，")
            for i in range(0, len(ll), 2):_m.append("，".join(ll[i:i+2]))
    _m = list(set(_m))

except Exception  as e:
    raise e

import random, time

def pickname():
    global _m
    random.seed(time.time())
    return random.choice(_m)
