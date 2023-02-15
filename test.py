from hint import CardRawData
import json
import random

from typing import TypeVar

with open("./resources/card copy.json", "r", encoding="utf8") as f:
    archived_Data: CardRawData = json.load(f)

T = TypeVar("T")


def delete_randomly(l: list[T], rate: float = 0.1) -> list[T]:
    """
    以rate的概率随机删除列表中的元素
    """
    return [i for i in l if random.random() > rate]


# save
with open("./resources/card.json", "w", encoding="utf8") as f:
    json.dump(delete_randomly(archived_Data), f, ensure_ascii=False, indent=4)