# pdf_parser: Обработка и извлечение данных из PDF файлов.
# Включает функции для чтения PDF, извлечения текстовых данных и их структурирования.

import pdfplumber
import os
import logging

from PaymentDocument_Class import PaymentDocument


def get_pdf_files(input_folder):
    # Получение списка PDF файлов из заданной папки.
    # Аргументы:
    #   input_folder (str): Путь к папке, содержащей PDF файлы.

    # Возвращает:
    #   List[str]: Список путей к PDF файлам в указанной папке.

    logging.info(f"Поиск PDF файлов в папке: {input_folder}")
    return [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]


def open_pdf_file(pdf_path):
    # Открытие PDF файла с использованием библиотеки pdfplumber.
    # Аргументы:
    #   pdf_path (str): Путь к PDF файлу.

    # Возвращает:
    #   pdfplumber.PDF: Объект PDF файла, открытый для чтения.

    return pdfplumber.open(pdf_path)


def process_pdf_file(filename, input_folder):
    # Обработка отдельного PDF файла и извлечение информации о платежных документах.
    # Аргументы:
    #   filename (str): Название PDF файла для обработки.
    #   input_folder (str): Путь к папке, содержащей PDF файл.

    # Возвращает:
    #   List[PaymentDocument]: Список объектов PaymentDocument, содержащих информацию из PDF файла.

    logging.info(f"Обработка PDF файла: {filename}")
    pdf_path = os.path.join(input_folder, filename)  # Получение полного пути к файлу
    documents = []
    with open_pdf_file(pdf_path) as pdf:  # Открытие PDF файла для чтения
        for page_number, page in enumerate(pdf.pages):
            doc = process_page(page, filename)  # Обработка каждой страницы PDF файла
            if doc:
                doc.file_path = pdf_path  # Сохранение пути к исходному PDF файлу в объекте PaymentDocument
                documents.append(doc)     # Добавление обработанного документа в список documents
    logging.info(f"Обработка PDF файла завершена: {filename}")
    return documents


def process_page(page, filename):
    # Обработка отдельной страницы PDF файла для извлечения информации о платежном документе.
    # Аргументы:
    #   page (pdfplumber.Page): Страница PDF файла.
    #   filename (str): Имя файла, из которого была получена страница.

    # Возвращает:
    #   PaymentDocument или None: Объект PaymentDocument с извлеченной информацией или None, если информация не найдена.

    word_categories = extract_words_from_page(page)  # Извлечение слов со страницы и их категоризация
    rects = determine_coordinates(word_categories)   # Определение координат для слов на странице
    doc = PaymentDocument()                          # Создание нового объекта PaymentDocument для хранения информации

    if rects is None:
        logging.error(f"В файле {filename} не найдены все необходимые данные.")
        return None

    # Извлечение информации о плательщике
    payer_info = extract_text_from_rect(page, rects.get('payer_rect'))
    payer_account_info = extract_text_from_rect(page, rects.get('payer_account_rect'))
    if payer_info:
        doc.payer = doc.process_entity_data(payer_info, payer_account_info)
        logging.info(f"Данные плательщика успешно извлечены:\n {doc.payer}")

    # Извлечение информации о получателе
    recipient_info = extract_text_from_rect(page, rects.get('recipient_rect'))
    recipient_account_info = extract_text_from_rect(page, rects.get('recipient_account_rect'))
    if recipient_info:
        doc.recipient = doc.process_entity_data(recipient_info, recipient_account_info)
        logging.info(f"Данные получателя успешно извлечены:\n {doc.recipient}")

    # Извлечение информации о получателе
    sum_info = extract_text_from_rect(page, rects.get('summa_rect'))
    if sum_info:
        doc.summa = doc.process_sum(sum_info)
        logging.info(f"Данные суммы успешно извлечены:\n {doc.summa}")

    # Извлечение номера платежного поручения
    number_info = extract_text_from_rect(page, rects.get('payment_number_rect'))
    if number_info:
        doc.number = doc.process_number(number_info)
        logging.info(f"Данные номера поручения успешно извлечены:\n {doc.number}")

    # Извлечение даты поступления документа
    admission_date_info = extract_text_from_rect(page, rects.get('admission_date_section_rect'))
    if admission_date_info:
        doc.admission_date = admission_date_info.strip()
        logging.info(f"Данные даты поступления успешно извлечены:\n {doc.admission_date}")

    # Извлечение назначения платежа
    purpose_info = extract_text_from_rect(page, rects.get('purpose_rect'))
    if purpose_info:
        doc.purpose = purpose_info.strip()
        logging.info(f"Данные назначения платежа успешно извлечены:\n {doc.purpose}")

    # Извлечение информации о банке плательщика
    payer_bank_info = extract_text_from_rect(page, rects.get('payer_bank_rect'))
    payer_bank_bik_info = extract_text_from_rect(page, rects.get('payer_bank_bik_rect'))
    payer_bank_account_info = extract_text_from_rect(page, rects.get('payer_bank_account_rect'))
    if payer_bank_info:
        doc.payer_bank = {'name': payer_bank_info, 'bik': payer_bank_bik_info,
                          'account': payer_bank_account_info}
        logging.info(f"Данные банка плательщика успешно извлечены:\n {doc.payer_bank}")

    # Извлечение информации о банке получателя
    recipient_bank_info = extract_text_from_rect(page, rects.get('recipient_bank_rect'))
    recipient_bank_bik_info = extract_text_from_rect(page, rects.get('recipient_bank_bik_rect'))
    recipient_bank_account_info = extract_text_from_rect(page, rects.get('recipient_bank_account_rect'))
    if recipient_bank_info:
        doc.recipient_bank = {'name': recipient_bank_info, 'bik': recipient_bank_bik_info,
                              'account': recipient_bank_account_info}
        logging.info(f"Данные банка получателя успешно извлечены:\n {doc.payer_bank}")

    # Извлечение даты списания средств
    debited_date_info = extract_text_from_rect(page, rects.get('debited_date_section_rect'))
    if debited_date_info:
        doc.debited_date = debited_date_info.strip()
        logging.info(f"Данные даты списания успешно извлечены:\n {doc.debited_date}")

    return doc


def extract_text_from_rect(page, rect):
    # Извлечение текста из определенного прямоугольника на странице PDF.
    # Аргументы:
    #   page (pdfplumber.Page): Страница PDF файла.
    #   rect (tuple): Координаты прямоугольника (x0, y0, x1, y1).

    # Возвращает:
    #   str или None: Извлеченный текст или None, если текст не найден.
    if rect:
        # Извлечение текста в указанных координатах прямоугольника
        extracted_text = page.within_bbox(rect).extract_text()

        # Удаление лишних пробелов из извлеченного текста и возврат результата
        return extracted_text.strip() if extracted_text else None
    return None


def extract_words_from_page(page):
    # Извлечение и категоризация слов со страницы PDF для последующего определения координат.
    # Аргументы:
    #   page (pdfplumber.Page): Страница PDF файла.

    # Возвращает:
    #   dict: Словарь с категориями слов и их координатами.

    logging.info(f"Извлечение координат.")
    words = page.extract_words()  # Извлечение списка слов с их координатами со страницы
    word_categories = {  # Ключи - категории информации, значения - извлеченные данные
        'payer': None, 'recipient': None, 'bik': [],
        'admission_date': None, 'number': None, 'inn': [], 'summa': [],
        'purpose': None, 'payer_bank': None,
        'recipient_bank': None, 'debited_date': None
    }

    # Ключ - слово для поиска. Значение - ключ из word_categories и действие ('append' или 'assign')
    category_mapping = {
        'ИНН': ('inn', 'append'),
        'Плательщик': ('payer', 'assign'),
        'Получатель': ('recipient', 'assign'),
        'БИК': ('bik', 'append'),
        'Поступ.': ('admission_date', 'assign'),
        'Сумма': ('summa', 'append'),
        'ПОРУЧЕНИЕ': ('number', 'assign'),
        'Назначение': ('purpose', 'assign'),
        'плательщика': ('payer_bank', 'assign'),
        'получателя': ('recipient_bank', 'assign'),
        'списано': ('debited_date', 'assign')
    }

    # Перебор всех слов на странице для категоризации в соответствии с category_mapping
    for word in words:
        word_text = word['text'].lower()
        found = False
        # Проверка, соответствует ли текст слова ключевым словам для категоризации
        for key, (category, action) in category_mapping.items():
            if word_text == key.lower():
                found = True
                process_word(word, category, action, word_categories)
                break
        if not found:
            # Если прямое соответствие не найдено, проверка на соответствие началу слова
            for key, (category, action) in category_mapping.items():
                if word_text.startswith(key.lower()):
                    process_word(word, category, action, word_categories)
                    break

    return word_categories


def process_word(word, category, action, word_categories):
    # Обработка слова для добавления в соответствующую категорию в word_categories.
    # Аргументы:
    #   word (dict): Слово и его координаты на странице.
    #   category (str): Категория, в которую нужно добавить слово.
    #   action (str): Тип действия ('append' или 'assign') для обработки слова.
    #   word_categories (dict): Словарь с категориями и данными слов.

    # Возвращает:
    #   None.

    # 'append' добавляет слово в список категории.
    if action == 'append':
        word_categories[category].append(word)
    # 'assign' присваивает слово напрямую категории
    elif action == 'assign':
        word_categories[category] = word


def determine_coordinates(word_categories):
    # Определение координат для ключевых категорий слов из PDF документа.
    # Аргументы:
    #   word_categories (dict): Словарь с категориями слов и их координатами.

    # Возвращает:
    #   dict: Словарь с координатами всех прямоугольников или None.

    logging.info(f"Определение областей для извлечения данных.")

    # Присваивание координат каждой категории слов
    inn_coordinates = word_categories['inn']
    payer_coordinates = word_categories['payer']
    recipient_coordinates = word_categories['recipient']
    bik_coordinates = word_categories['bik']
    admission_date_coordinates = word_categories['admission_date']
    summa_coordinates = word_categories['summa']
    number_coordinates = word_categories['number']
    purpose_coordinates = word_categories['purpose']
    payer_bank_coordinates = word_categories['payer_bank']
    recipient_bank_coordinates = word_categories['recipient_bank']
    debited_date_coordinates = word_categories['debited_date']

    # Проверка наличия всех необходимых координат для создания прямоугольников
    if (len(inn_coordinates) >= 2 and payer_coordinates and recipient_coordinates and len(bik_coordinates) >= 2 and
            admission_date_coordinates and len(summa_coordinates) >= 2 and number_coordinates and purpose_coordinates
            and payer_bank_coordinates and recipient_bank_coordinates and debited_date_coordinates):
        logging.info(f"Все координаты получены.")
        rect_definitions = {  # Ключ - название прямоугольника, значения - координаты и смещения для каждой стороны
            'payer_rect': {
                'left': [payer_coordinates['x0'], -10], 'right': [bik_coordinates[0]['x0'], -3],
                'top': [inn_coordinates[0]['top'], -3], 'bottom': [payer_coordinates['bottom'], -10]
            },
            'recipient_rect': {
                'left': [recipient_coordinates['x0'], -10], 'right': [bik_coordinates[0]['x0'], -3],
                'top': [inn_coordinates[1]['top'], -3], 'bottom': [recipient_coordinates['bottom'], -10]
            },
            'admission_date_section_rect': {
                'left': [admission_date_coordinates['x0'], 0], 'right': [admission_date_coordinates['x1'], 40],
                'top': [admission_date_coordinates['top'], -20], 'bottom': [admission_date_coordinates['bottom'], -10]
            },
            'summa_rect': {
                'left': [summa_coordinates[1]['x0'], 35], 'right': [summa_coordinates[1]['x1'], 100],
                'top': [summa_coordinates[1]['top'], -5], 'bottom': [summa_coordinates[1]['bottom'], 20]
            },
            'payment_number_rect': {
                'left': [number_coordinates['x0'], 55], 'right': [number_coordinates['x1'], 70],
                'top': [number_coordinates['top'], -5], 'bottom': [number_coordinates['bottom'], 5]
            },
            'purpose_rect': {
                'left': [purpose_coordinates['x0'], 0], 'right': [purpose_coordinates['x1'], 480],
                'top': [recipient_coordinates['bottom'], 10], 'bottom': [purpose_coordinates['bottom'], -15]
            },
            'payer_bank_rect': {
                'left': [payer_bank_coordinates['x0'], -30], 'right': [bik_coordinates[0]['x0'], -3],
                'top': [payer_coordinates['bottom'], 0], 'bottom': [payer_bank_coordinates['bottom'], -10]
            },
            'recipient_bank_rect': {
                'left': [recipient_bank_coordinates['x0'], -30], 'right': [bik_coordinates[0]['x0'], -3],
                'top': [payer_bank_coordinates['bottom'], 0], 'bottom': [recipient_bank_coordinates['bottom'], -10]
            },
            'debited_date_section_rect': {
                'left': [debited_date_coordinates['x0'], 0], 'right': [debited_date_coordinates['x1'], 40],
                'top': [debited_date_coordinates['top'], -20], 'bottom': [debited_date_coordinates['bottom'], -10]
            },
            'payer_bank_bik_rect': {
                'left': [bik_coordinates[0]['x0'], 35], 'right': [bik_coordinates[0]['x1'], 100],
                'top': [payer_coordinates['top'], 0], 'bottom': [bik_coordinates[0]['bottom'], 5]
            },
            'payer_bank_account_rect': {
                'left': [bik_coordinates[0]['x0'], 35], 'right': [bik_coordinates[0]['x1'], 155],
                'top': [bik_coordinates[0]['bottom'], 0], 'bottom': [bik_coordinates[1]['top'], -10]
            },
            'recipient_bank_bik_rect': {
                'left': [bik_coordinates[1]['x0'], 35], 'right': [bik_coordinates[1]['x1'], 100],
                'top': [bik_coordinates[1]['top'], -5], 'bottom': [bik_coordinates[1]['bottom'], 5]
            },
            'recipient_bank_account_rect': {
                'left': [bik_coordinates[1]['x0'], 35], 'right': [bik_coordinates[1]['x1'], 155],
                'top': [bik_coordinates[1]['top'], 10], 'bottom': [bik_coordinates[1]['bottom'], 30]
            },
            'payer_account_rect': {
                'left': [bik_coordinates[0]['x0'], 35], 'right': [bik_coordinates[0]['x1'], 155],
                'top': [payer_coordinates['top'], -40], 'bottom': [payer_coordinates['bottom'], 0]
            },
            'recipient_account_rect': {
                'left': [bik_coordinates[1]['x0'], 35], 'right': [bik_coordinates[1]['x1'], 155],
                'top': [bik_coordinates[1]['top'], 41], 'bottom': [bik_coordinates[1]['bottom'], 61]
            }
        }
        rects = {}
        for name, sides in rect_definitions.items():
            # Расчет координат для каждого прямоугольника в rect_definitions
            left, top = sides['left'][0] + sides['left'][1], sides['top'][0] + sides['top'][1]
            right, bottom = sides['right'][0] + sides['right'][1], sides['bottom'][0] + sides['bottom'][1]
            rects[name] = (left, top, right, bottom)  # Сохранение координат в словаре rects

        return rects
    logging.error(f"Не удалось определить все области.")
    return None


def parser_main(input_folder):
    # Основная функция парсера для обработки PDF файлов в указанной папке.
    # Аргументы:
    #   input_folder (str): Путь к папке с PDF файлами.

    # Возвращает:
    #   list: Список обработанных документов

    documents = []
    for filename in get_pdf_files(input_folder):  # Цикл обработки каждого PDF файла в папке
        documents += process_pdf_file(filename, input_folder)  # Добавление обработанных документов в список

    return documents
