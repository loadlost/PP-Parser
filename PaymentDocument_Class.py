# PaymentDocument_Class: Класс для представления и обработки платежных документов.
# Включает методы для обработки данных плательщика, получателя, банков, суммы платежа,
# номера документа и создания уникального идентификатора.

import re


class PaymentDocument:
    # Содержит информацию о плательщике, получателе, банках, сумме и другие детали платежа.

    def __init__(self):
        self.payer = {  # Информация о плательщике
            "name": None,
            "inn": None,
            "kpp": None,
            "account": None
        }
        self.recipient = {  # Информация о получателе
            "name": None,
            "inn": None,
            "kpp": None,
            "account": None
        }
        self.payer_bank = {  # Банк плательщика
            "name": None,
            "bik": None,
            "account": None
        }
        self.recipient_bank = {  # Банк получателя
            "name": None,
            "bik": None,
            "account": None
        }
        self.summa = None
        self.admission_date = None
        self.debited_date = None
        self.number = None
        self.purpose = None
        self.file_path = None
        self.unique_identifier = None  # Уникальный идентификатор документа

    @staticmethod
    def process_entity_data(entity_str, account_info):
        # Обработка строковых данных сущности и извлечение информации о названии, ИНН, КПП и банковском счете.
        # Аргументы:
        #   entity_str (str): Строка с информацией о сущности (например, плательщике или получателе).
        #   account_info (str): Информация о банковском счете сущности.

        # Возвращает:
        #   dict: Словарь с извлеченной информацией о сущности

        entity_data = {
            "name": None,
            "inn": None,
            "kpp": None,
            "account": account_info
        }

        # Поиск и извлечение ИНН и КПП из строки
        inn_match = re.search(r'ИНН (\d+)', entity_str)
        kpp_match = re.search(r'КПП (\d+)', entity_str)

        if inn_match:
            entity_data['inn'] = inn_match.group(1)
        if kpp_match:
            entity_data['kpp'] = kpp_match.group(1)

        # Очистка строки от ИНН и КПП для извлечения названия
        name_part = entity_str
        if inn_match:
            name_part = re.split(r'ИНН \d+', name_part)[-1]
        if kpp_match:
            name_part = re.split(r'КПП \d+', name_part)[-1]
        else:
            name_part = re.sub(r'КПП', '', name_part)

        entity_data['name'] = name_part.strip()

        return entity_data

    @staticmethod
    def process_sum(sum_str):
        # Обработка строки суммы для преобразования в числовой формат.
        # Аргументы:
        #   sum_str (str): Строка, представляющая сумму денег.

        # Возвращает:
        #   float: Числовое представление суммы

        sum_str = sum_str.replace('-', '.')  # Замена тире на точку
        cleaned_sum = re.sub(r'[^\d.]', '', sum_str)  # Удаление всех нечисловых символов
        return float(cleaned_sum)  # Преобразование в числовой формат и возврат

    @staticmethod
    def process_number(number_str):
        # Обработка строки номера для преобразования в формат без буквенных символов.
        # Аргументы:
        #   number_str (str): Строка, содержащая номер.

        # Возвращает:
        #   str: Очищенный от букв номер

        cleaned_number = re.sub(r'\D', '', number_str)  # Удаление всех нечисловых символов
        return cleaned_number

    def clean_newlines(self):
        # Удаление переносов строк и сокращение длинных названий в данных плательщика, получателя и банков.
        # Аргументы:
        #   self: Экземпляр класса PaymentDocument.

        # Возвращает:
        #   None: Производится изменение в атрибутах объекта на месте

        for attr in [self.payer, self.recipient, self.payer_bank, self.recipient_bank]:
            updated_attr = {}
            for key, value in attr.items():  # Перебор ключей и значений в каждом атрибуте
                if isinstance(value, str):
                    # Сокращение длинного названия
                    value = re.sub(r'общество\s+с\s+ограниченной\s*ответственностью', 'ООО', value, flags=re.IGNORECASE)

                    value = value.replace('\n', '')  # Удаление переносов строк
                updated_attr[key] = value  # Добавление обновленного значения в словарь
            attr.clear()
            attr.update(updated_attr)  # Обновление оригинального словаря новыми значениями

        if isinstance(self.purpose, str):
            self.purpose = self.purpose.replace('\n', '')  # Удаление переносов строк в назначении платежа

