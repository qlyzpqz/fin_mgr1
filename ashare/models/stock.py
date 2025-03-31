from dataclasses import dataclass
from datetime import date

@dataclass
class Stock:
    ts_code: str
    symbol: str
    name: str
    area: str
    industry: str
    fullname: str
    enname: str
    cnspell: str
    market: str
    exchange: str
    curr_type: str
    list_status: str
    list_date: date
    delist_date: date
    is_hs: str
    act_name: str
    act_ent_type: str