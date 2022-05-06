# import sqlite3
# import datetime
# from pathlib import Path
#
#
# class Database:
#     def __init__(self, path: str):
#         self.path = Path(path)
#         self.connection = sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
#         self.cursor = self.connection.cursor()
#         self.create_table_if_not_exists()
#
#     def connect(self):
#         return sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
#
#     def create_table_if_not_exists(self):
#         print('creating')
#         self.cursor.execute('''
#         create table if not exists notes (
#             id integer primary key not null,
#             timestamp timestamp not null,
#             text text not null
#         )
#         ''')
#         self.connection.commit()
#
#     def insert(self, text: str) -> None:
#         timestamp = datetime.datetime.now()
#         self.cursor.execute('insert into notes(timestamp, text) values (?, ?)', (timestamp, text))
#         self.connection.commit()
#
#     def get_all(self):
#         self.cursor.execute('select * from notes order by timestamp desc')
#         return self.cursor.fetchall()
#
#     # def updateData(self, id: int, data: list):
#     #     self.cursor.execute(
#     #         f"UPDATE products SET name='{data[0]}', price={data[1]}, stock={data[2]}, eatable={data[3]} WHERE id={id}")
#     #     self.connection.commit()
#     #
#     # def deleteOFromDb(self, id: int):
#     #     self.cursor.execute(f"DELETE FROM products WHERE id = {id}")
#     #     self.connection.commit()
#
#     def close(self):
#         self.connection.close()


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
