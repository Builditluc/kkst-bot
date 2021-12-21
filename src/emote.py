from dataclasses import dataclass
from typing import Dict

from nextcord.partial_emoji import PartialEmoji
from nextcord.reaction import Reaction

__all__ = ["EMOTES", "Emote"]


@dataclass
class Emote:
    content: str

    @property
    def emoij(self) -> PartialEmoji:
        return PartialEmoji(name=self.content)

    def __str__(self) -> str:
        return self.content

    def __eq__(self, other) -> bool:
        if isinstance(other, Reaction):
            return str(other.emoji) == self.content

        return super().__eq__(other)


EMOTES: Dict[str, Emote] = {
    # check
    "white_check_mark": Emote("✅"),
    "x": Emote("❌"),
    # numbers
    "one": Emote("1️⃣"),
    "two": Emote("2️⃣"),
    "three": Emote("3️⃣"),
}
