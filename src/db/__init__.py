from db.exam import ExamInterface

__all__ = ["EXAMS_DATABASE"]

EXAMS_DATABASE = ExamInterface(
    host="db", username="root", password="supersecretpassword", database="kkst"
)
