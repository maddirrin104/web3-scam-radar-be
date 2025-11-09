from dataclasses import dataclass


@dataclass
class RuleHit:
code: str
reason: str
weight: int


LEVELS = [
(0, "LOW"), (20, "MEDIUM"), (50, "HIGH"), (80, "CRITICAL")
]


def level_from_score(score: int) -> str:
lvl = "LOW"
for th, name in LEVELS:
if score >= th:
lvl = name
return lvl