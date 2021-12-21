from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from nextcord.embeds import Embed

__all__ = [
    "Exam",
    "ExamTopic",
    "EXAM_SCHEMA",
    "EXAM_FIELDS",
    "EXAM_TOPIC_SCHEMA",
    "EXAM_TOPIC_FIELDS",
]


EXAM_SCHEMA = "(id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(255) UNIQUE, date DATE, message_id VARCHAR(255))"
EXAM_FIELDS = "name, date, message_id"

EXAM_TOPIC_SCHEMA = "(id INT PRIMARY KEY AUTO_INCREMENT, title VARCHAR(255), exam_id INT, FOREIGN KEY(exam_id) REFERENCES exams(id), content VARCHAR(1000))"
EXAM_TOPIC_FIELDS = "title, exam_id, content"


@dataclass
class ExamTopic:
    title: str
    content: List[str]

    def toString(self) -> str:
        return "\n".join(self.content)

    @staticmethod
    def fromString(topic: str):
        """
        parse strings in this format:

        [t]Topic 1:
        [c]- topic 1.1
        [c]- topic 1.2
        [t]Topic 2:
        ...
        """
        topics: List[ExamTopic] = []
        current_topic: Optional[ExamTopic] = None

        for string in topic.splitlines(keepends=False):
            if string.startswith("[t]"):
                if current_topic is not None:
                    topics.append(current_topic)
                    current_topic = None
                current_topic = ExamTopic(title=string.lstrip("[t]"), content=[])
            elif string.startswith("[c]"):
                if current_topic is None:
                    continue
                current_topic.content.append(string.lstrip("[c]"))

        if current_topic is not None:
            topics.append(current_topic)

        return topics


@dataclass
class Exam:
    name: str
    topics: List[ExamTopic]
    date: datetime
    messageId: int

    def toEmbed(self) -> Embed:
        embed = Embed(title=self.name, type="rich", timestamp=self.date)

        topics_without_content: List[str] = []

        for topic in self.topics:
            if len(topic.content) == 0:
                topics_without_content.append(topic.title)
                continue

            embed.add_field(name=topic.title, value="\n".join(topic.content))

        if len(topics_without_content) > 0:
            embed.insert_field_at(
                0, name="Themen:", value="\n".join(topics_without_content)
            )

        return embed
