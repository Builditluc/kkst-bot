from typing import Dict
from dataclasses import dataclass

from nextcord.partial_emoji import PartialEmoji
from nextcord.reaction import Reaction

@dataclass
class Emote:
    unicode: str

    @property
    def emoji(self) -> PartialEmoji:
        return PartialEmoji(name=self.unicode)

    def __str__(self) -> str:
        return self.unicode

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Reaction):
            return str(other.emoji) == self.unicode

        return super().__eq__(other)


CHECK: Dict[str, Emote] = {
    "white_check_mark": Emote("✅"),
    "x": Emote("❌"),
}

NUMBERS: Dict[str, Emote] = {
    "one": Emote("1️⃣"),
    "two": Emote("2️⃣"),
    "three": Emote("3️⃣"),
}
