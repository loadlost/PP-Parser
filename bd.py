# bd: Создание и управление базой данных.
# Включает функционал для создания базы данных и таблиц, а также для работы с данными документа.

import logging

from sqlalchemy import create_engine, Column, Integer, String, Date, DECIMAL
from sqlalchemy.dialects.mysql import LONGBLOB

from sqlalchemy.orm import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()


class Document(Base):
    # Определяет структуру таблицы 'documents'.

    __tablename__ = 'documents'  # Название таблицы в базе данных

    id = Column(Integer, primary_key=True)  # Идентификатор документа
    number = Column(Integer)
    admission_date = Column(Date)
    debited_date = Column(Date)
    payer_name = Column(String(255))
    payer_inn = Column(String(255))
    payer_kpp = Column(String(255))
    payer_account = Column(String(255))
    recipient_name = Column(String(255))
    recipient_inn = Column(String(255))
    recipient_kpp = Column(String(255))
    recipient_account = Column(String(255))
    summa = Column(DECIMAL(10, 2))
    payer_bank_name = Column(String(255))
    payer_bank_bik = Column(String(255))
    payer_bank_account = Column(String(255))
    recipient_bank_name = Column(String(255))
    recipient_bank_bik = Column(String(255))
    recipient_bank_account = Column(String(255))
    purpose = Column(String(255))
    unique_identifier = Column(String(255), unique=True)  # Уникальный идентификатор документа
    file_path = Column(String(255))
    file_content = Column(LONGBLOB)  # Содержимое файла документа в бинарном формате

    def generate_unique_identifier(self):
        # Генерация уникального идентификатора документа на основе его номера, даты, имен плательщика и получателя.
        # Аргументы:
        #   self: Экземпляр класса Document.

        # Возвращает:
        #   None: Уникальный идентификатор устанавливается как атрибут объекта

        if self.number and self.admission_date and self.payer_name and self.recipient_name:
            formatted_date = self.admission_date.strftime("%d.%m.%Y") if self.admission_date else None

            self.unique_identifier = f"ПП №{self.number} от {formatted_date} {self.payer_name}/{self.recipient_name}"
        else:
            self.unique_identifier = None  # Идентификатор не устанавливается, если отсутствуют ключевые данные


engine = create_engine('mysql+mysqlconnector://root:password@localhost/')

# Попытка создания базы данных (если еще не существует)
try:
    with engine.connect() as connection:
        connection.execute(text("CREATE DATABASE IF NOT EXISTS PPDB"))
except SQLAlchemyError as e:
    logging.error(f"Ошибка при создании базы данных: {e}")

# Создание нового движка для подключения к конкретной базе данных
engine = create_engine('mysql+mysqlconnector://root:password@localhost/PPDB')

# Попытка создания таблицы (если она еще не существует)
try:
    if not inspect(engine).has_table("documents"):
        Base.metadata.create_all(engine)
except SQLAlchemyError as e:
    logging.error(f"Ошибка при создании таблицы: {e}")
