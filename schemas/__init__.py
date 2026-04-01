from dataclasses import dataclass


# 一些公共的schemas可以放在这里
@dataclass
class BasePaging :
    pno: int = 1
    page_size: int = 10