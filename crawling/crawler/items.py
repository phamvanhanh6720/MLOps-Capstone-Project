import scrapy
import datetime
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class BonBanhRawItem:
    title: Optional[str]
    url: Optional[str]
    year: Optional[str]
    price: Optional[str]
    location: Optional[str]

    branch: Optional[str]
    model: Optional[str]
    raw_origin: Optional[str]
    raw_km_driven: Optional[str]

    external_color: Optional[str]
    internal_color: Optional[str]
    num_seats: Optional[str]
    engine_info: Optional[str]

    gearbox: Optional[str]
    wheel_drive: Optional[str]
    car_type: Optional[str]
    raw_post_date: Optional[str]


@dataclass
class BonBanhItem:
    title: Optional[str]
    url: Optional[str]
    year: Optional[int]
    price: Optional[float]
    location: Optional[str]

    branch: Optional[str]
    model: Optional[str]
    origin: Optional[str]
    km_driven: Optional[float]

    external_color: Optional[str]
    internal_color: Optional[str]
    num_seats: Optional[int]
    fuels: Optional[str]

    engine_capacity: Optional[float]
    gearbox: Optional[str]
    wheel_drive: Optional[str]
    car_type: Optional[str]
    post_date: Optional[datetime.date]