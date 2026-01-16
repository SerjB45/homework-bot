import logging
import os
import sys
import time
from http import HTTPStatus
from json.decoder import JSONDecodeError

import requests
from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import (ChatIDNotFound, ConvertationError, DateRequestError,
                        HomeworkError, HTTPRequestOthersError,
                        HTTPRequestStatusError, MessageNotSend,
                        ResponseTypeError, TokenNotFound, UnknowStatusHomework)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Функция по проверке токенов."""
    tokens = {
        'PRACTICUM_TOKEN': [PRACTICUM_TOKEN, TokenNotFound],
        'TELEGRAM_TOKEN': [TELEGRAM_TOKEN, TokenNotFound],
        'TELEGRAM_CHAT_ID': [TELEGRAM_CHAT_ID, ChatIDNotFound],
    }
    for key, values in tokens.items():
        if not values[0]:
            raise values[1](key)


def send_message(bot, message):
    """Отправка сообщения ботом."""
    logging.info('Отправка сообщения в Telegram')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        raise MessageNotSend(error)
    else:
        logging.debug('Сообщение успешно отправлено')


def get_api_answer(timestamp):
    """Получение данных от сервиса."""
    payload = {'from_date': timestamp}
    try:
        logging.info(
            f'Запрос к API сервиса.'
            f'Параметры запроса: {ENDPOINT}\n{HEADERS}\n{payload}'
        )
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except Exception as error:
        raise HTTPRequestOthersError(error, response.status_code)

    if response.status_code != HTTPStatus.OK:
        raise HTTPRequestStatusError(f'Эндпоинт {response.url} недоступен.')

    try:
        response = response.json()
    except JSONDecodeError as error:
        raise ConvertationError(
            f'Ошибка при конвертации ответа в JSON: {error}'
        )

    return response


def check_response(response):
    """Проверка ответа API."""
    if not isinstance(response, dict):
        raise ResponseTypeError(
            'response',
            'Аргумент не является словарем. Проверьте ответ API'
        )

    homeworks = response.get('homeworks')
    current_date = response.get('current_date')
    if homeworks is None:
        raise HomeworkError(
            'Ответ API не соответсвует ожидаемому. '
            'Не получены данные по домашней работе'
        )
    if current_date is None:
        raise DateRequestError()

    if not isinstance(homeworks, list):
        raise ResponseTypeError(
            'homeworks',
            'У списка домашних работ неверный тип данных'
        )

    return homeworks


def parse_status(homework):
    """Парсинг статуса работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None:
        raise HomeworkError('В ответе API нет названия работы')
    if homework_status not in HOMEWORK_VERDICTS:
        raise UnknowStatusHomework()

    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    try:
        check_tokens()
    except Exception as error:
        logging.critical(error)
        logging.critical('Бот Остановлен!')
        sys.exit()

    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                status = parse_status(homeworks[0])
                send_message(bot, status)
            else:
                logging.debug('Нет новых статусов домашних работ')
            timestamp = response.get('current_date', timestamp)
        except MessageNotSend:
            logging.error('Ошибка отправки сообщения')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler('homeworkbot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    main()
