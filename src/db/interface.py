from typing import List, Optional, Tuple
import mysql.connector as mysql

class DatabaseInterface:
    def __init__(self, host: str, user: str, password: str):
        self.connection = mysql.MySQLConnection(host=host, user=user, password=password)

        self.table_name: str
        self.schema: str
        
    def connect(self, database_name: str):
        cursor = self.connection.cursor()
        for database in self.list_databases(cursor):
            if database[0] == database_name:
                self.connection.database = database
                return
        self.create_database(cursor, database_name)
        self.connection.database = database_name

    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} {self.schema}")

    def drop_table(self):
        cursor = self.connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")

    @staticmethod
    def list_databases(cursor) -> List[Tuple[str,]]:
        cursor.execute("SHOW DATABASES")
        return cursor.fetchall()

    @staticmethod
    def create_database(cursor, database_name):
        cursor.execute(f"CREATE_DATABASE {database_name}")

    def insert(self, fields: str, value: Tuple) -> str:
        cursor = self.connection.cursor()
        cursor.execute(f"INSERT INTO {self.table_name}({fields}) VALUES{value};")
        cursor.execute("SELECT LAST_INSERT_ID();")
        return cursor.fetchone()[0]

    def insert_many(self, fields: str, values: List[Tuple]) -> List[str]:
        output: List[str] = []
        for value in values:
            output.append(self.insert(fields, value))
        return output

    def select(self, filter: Optional[str] = None) -> List[Tuple]:
        cursor = self.connection.cursor()
        command = f"SELECT * FROM {self.table_name}"
        if filter:
            command += f" WHERE {filter}"
        cursor.execute(command)
        return cursor.fetchall()

    def remove(self, filter: str):
        cursor = self.connection.cursor()
        cursor.execute(f"DELETE FROM {self.table_name} WHERE {filter}")
