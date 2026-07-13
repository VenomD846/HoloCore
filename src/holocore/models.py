from dataclasses import dataclass


@dataclass(frozen=True)
class Result:
    source: str
    title: str
    text: str
    location: str
