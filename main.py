# main — точка входа приложения, координирующей процесс чтения, обработки PDF-документов,
# создания DataFrame и их сохранения в базу данных.

import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine

import pdf_parser
import dataframe
import bd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d.%m.%Y %H:%M:%S')


def create_session(con_string):
    # Создание и возвращение сессии SQLAlchemy для работы с базой данных.
    # Аргументы:
    #   con_string (str): Строка подключения к базе данных.

    # Возвращает:
    #   sqlalchemy.orm.session.Session: Экземпляр сессии, связанный с заданным движком базы данных.

    logging.info(f"Создание сессии SQL для {con_string}")
    engine = create_engine(con_string)   # Создание движка SQLAlchemy с указанной строкой подключения
    session = sessionmaker(bind=engine)  # Создание сессии SQLAlchemy, связанной с движком
    return session()                     # Возвращение экземпляра сессии


def save_to_database(df, con_string):
    # Сохранение данных из DataFrame в базу данных.
    # Аргументы:
    #   df (pandas.DataFrame): DataFrame содержащий данные для сохранения.
    #   con_string (str): Строка подключения к базе данных.

    # Возвращает:
    #   None

    logging.info("Начало сохранения данных в базу данных")
    session = create_session(con_string)

    for index, row in df.iterrows():
        try:
            document = bd.Document()
            # Присвоение значений каждому атрибуту документа из строки DataFrame
            for column in df.columns:
                setattr(document, column, row[column])

            document.generate_unique_identifier()  # Генерация уникального идентификатора для документа
            session.add(document)                  # Добавление документа в сессию
            session.commit()                       # Фиксация изменений в базе данных
            logging.info(f"Документ {document.file_path} сохранен в базу данных")

        except IntegrityError as e:
            logging.error(f"Ошибка целостности данных в файле {row['file_path']}: {e.orig.msg}")
            session.rollback()  # Откат изменений из-за ошибки
            continue

        except Exception as e:
            logging.error(f"Общая ошибка в файле {row['file_path']}: {str(e)}")
            session.rollback()  # Откат изменений из-за ошибки
            continue

    session.close()  # Закрытие сессии после завершения всех операций
    logging.info("Сохранение данных в базу данных завершено")


def main():
    # Основная функция приложения.
    # Считывает документы, создает DataFrame и сохраняет данные в базу данных.

    input_folder = 'input'  # Папка, из которой будут считываться PDF документы
    documents = pdf_parser.parser_main(input_folder)  # Обработка PDF документов

    df = dataframe.create_dataframe(documents)  # Создание DataFrame из обработанных документов

    save_to_database(df, 'mysql+mysqlconnector://root:password@localhost/PPDB')  # Сохранение данных в базу данных


if __name__ == "__main__":
    main()
