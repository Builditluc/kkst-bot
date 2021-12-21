from typing import List, Tuple, Optional
from datetime import datetime
from db.exam.model import (
    EXAM_FIELDS,
    EXAM_SCHEMA,
    EXAM_TOPIC_FIELDS,
    EXAM_TOPIC_SCHEMA,
    Exam,
    ExamTopic,
)
from db.interface import DatabaseInterface
from log import LogLevel, init_logger

__all__ = ["ExamInterface"]

log = init_logger(__name__, LogLevel.DEBUG)


class ExamTopicInterface(DatabaseInterface):
    def __init__(self, host: str, username: str, password: str, database: str) -> None:
        super().__init__(host, username, password, EXAM_TOPIC_SCHEMA, "exam_topics")

        self.connect(database)
        self.createTable()


class ExamInterface(DatabaseInterface):
    def __init__(self, host: str, username: str, password: str, database: str) -> None:
        super().__init__(host, username, password, EXAM_SCHEMA, "exams")

        self.connect(database)
        self.createTable()

        self.topicInterface = ExamTopicInterface(host, username, password, database)

    def createExam(self, exam: Exam):
        log.info(f"Inserting the exam {exam=} into the database")
        exam_id = self.insert(
            EXAM_FIELDS,
            (exam.name, exam.date.strftime("%Y-%m-%d %H:%M:%S"), str(exam.messageId)),
        )
        for topic in exam.topics:
            self.topicInterface.insert(
                EXAM_TOPIC_FIELDS, (topic.title, exam_id, topic.toString())
            )

    def removeExam(self, name: str):
        log.info(f"Removing the exam {name=} from the database")
        exam_id = self.get(f"name='{name}'")[0][0]
        self.remove(f"name='{name}'")
        self.topicInterface.remove(f"exam_id={exam_id}")

    def getExam(self, name: str) -> Optional[Exam]:
        log.info(f"Fetching the exam {name=} from the database")
        exams = self.get(f"name='{name}'")
        if len(exams) == 0:
            return None
        raw_topics = self.topicInterface.get(f"exam_id={exams[0][0]}")
        topics: List[ExamTopic] = []
        for raw_topic in raw_topics:
            topics.append(
                ExamTopic(title=raw_topic[0], content=raw_topic[2].splitlines())
            )
        log.debug(f"Topics for the exam '{exams[0]}': {topics=}")
        return Exam(
            name=exams[0][1],
            topics=topics,
            date=datetime.combine(exams[0][2], datetime.min.time()),
            messageId=exams[0][3],
        )

    def getAllExams(self) -> List[Exam]:
        log.info(f"Fetching all exams from the database")
        raw_exams: List[Tuple] = self.get(None)

        exams: List[Exam] = []
        for raw_exam in raw_exams:
            raw_topics = self.topicInterface.get(f"exam_id={raw_exam[0]}")
            topics: List[ExamTopic] = []
            for raw_topic in raw_topics:
                topics.append(
                    ExamTopic(title=raw_topic[0], content=raw_topic[2].splitlines())
                )
            log.debug(f"Topics for the exam '{raw_exam[1]}': {topics=}")
            exams.append(
                Exam(
                    name=raw_exam[1], topics=[], date=raw_exam[2], messageId=raw_exam[3]
                )
            )
        return exams
