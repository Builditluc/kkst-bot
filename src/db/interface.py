from typing import List, Optional, Tuple
import mysql.connector as mysql

from log import init_logger, LogLevel

__all__ = ["DatabaseInterface"]

log = init_logger(__name__, LogLevel.DEBUG)


class DatabaseInterface:
    def __init__(
        self, host: str, username: str, password: str, schema: str, table_name: str
    ) -> None:
        self.connection = mysql.MySQLConnection(
            host=host, user=username, password=password
        )
        self.schema = schema
        self.table_name = table_name

    def __del__(self):
        log.info("Closing the database connection")
        self.connection.close()

    def connect(self, db_name: str):
        cursor = self.connection.cursor()
        for database in self.list_databases(cursor):
            if database[0] == db_name:
                self.connection.database = database
                return
        self.createDatabase(cursor, db_name)
        self.connection.database = db_name

    @staticmethod
    def list_databases(cursor) -> List[Tuple[str,]]:
        cursor.execute("SHOW DATABASES")
        return cursor.fetchall()

    @staticmethod
    def createDatabase(cursor, database_name):
        cursor.execute(f"CREATE DATABASE {database_name}")

    def createTable(self):
        cursor = self.connection.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} {self.schema}")
        cursor.close()

    def dropTable(self):
        cursor = self.connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        cursor.close()

    def insert(self, fields: str, value: Tuple):
        cursor = self.connection.cursor()
        cursor.execute(f"INSERT INTO {self.table_name}({fields}) VALUES {value};")
        cursor.execute(f"SELECT LAST_INSERT_ID();")
        last_id = cursor.fetchone()[0]

        self.connection.commit()
        return last_id

    def insertMany(self, fields: str, values: List[Tuple]):
        output: List[str] = []
        for value in values:
            output.append(self.insert(fields, value))
        return output

    def get(self, filter: Optional[str]) -> List[Tuple]:
        cursor = self.connection.cursor()
        command = f"SELECT * FROM {self.table_name}"
        if filter:
            command += f" WHERE {filter}"
        log.debug(f"Executing {command=}")
        cursor.execute(command)
        return cursor.fetchall()

    def remove(self, filter: str):
        cursor = self.connection.cursor()
        command = f"DELETE FROM {self.table_name} WHERE {filter}"
        log.debug(f"Executing {command=}")
        cursor.execute(command)
        self.connection.commit()
        cursor.close()
