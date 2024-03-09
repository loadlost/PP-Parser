# dataframe: Создание и обработка DataFrame.
# Включает функции для чтения файлов, преобразования данных в формат DataFrame.


import pandas as pd
from datetime import datetime


def create_dataframe(documents):
    # Создание DataFrame из списка обработанных платежных документов.
    # Аргументы:
    #   documents (list): Список экземпляров класса PaymentDocument.

    # Возвращает:
    #   DataFrame: Pandas DataFrame с данными из платежных документов

    data = []

    for doc in documents:  # Перебор документов для обработки
        doc.clean_newlines()  # Очистка данных документа от переносов строк

        # Добавление данных документа в список
        data.append({
            'number': doc.number,
            'admission_date': datetime.strptime(doc.admission_date, '%d.%m.%Y') if doc.admission_date else None,
            'debited_date': datetime.strptime(doc.debited_date, '%d.%m.%Y')if doc.debited_date else None,
            'payer_name': doc.payer.get('name'),
            'payer_inn': doc.payer.get('inn'),
            'payer_kpp': doc.payer.get('kpp'),
            'payer_account': doc.payer.get('account'),
            'recipient_name': doc.recipient.get('name'),
            'recipient_inn': doc.recipient.get('inn'),
            'recipient_kpp': doc.recipient.get('kpp'),
            'recipient_account': doc.recipient.get('account'),
            'summa': doc.summa,
            'payer_bank_name': doc.payer_bank.get('name'),
            'payer_bank_bik': doc.payer_bank.get('bik'),
            'payer_bank_account': doc.payer_bank.get('account'),
            'recipient_bank_name': doc.recipient_bank.get('name'),
            'recipient_bank_bik': doc.recipient_bank.get('bik'),
            'recipient_bank_account': doc.recipient_bank.get('account'),
            'purpose': doc.purpose,
            'file_path': doc.file_path,
            'unique_identifier': doc.unique_identifier,
            'file_content': read_file_content(doc.file_path)    # Чтение содержимого файла документа
        })

    df = pd.DataFrame(data)  # Создание DataFrame из списка данных

    return df


def read_file_content(file_path):
    # Чтение содержимого файла по указанному пути.
    # Аргументы:
    #   file_path (str): Путь к файлу.

    # Возвращает:
    #   bytes: Содержимое файла в бинарном формате

    with open(file_path, 'rb') as file:
        file_content = file.read()
    return file_content
