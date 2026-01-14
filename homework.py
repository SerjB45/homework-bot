import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import MessageNotSend, TokenNotFound, UnknowStatusHomework

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
    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN]):
        raise TokenNotFound('Проверьте токены!')
    if not TELEGRAM_CHAT_ID:
        raise TokenNotFound('Проверьте ID чата!')


def send_message(bot, message):
    """Отправка сообщения ботом."""
    logging.info('Отправка сообщения в Telegram')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(f'Не удалось отправить сообщение: {error}')
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
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError(
                f'Ошибка при запросе к API: '
                f'код ответа {response.status_code}'
            )

    except Exception as error:
        logging.error(f'Ошибка при запросе к API: {error}')
        raise ConnectionError(f'Ошибка при запросе к API: {error}')

    return response.json()


def check_response(response):
    """Проверка ответа сервера."""
    if not isinstance(response, dict):
        raise TypeError('Аргумент не является словарем')
    homeworks = response.get('homeworks')
    current_date = response.get('current_date')
    if homeworks is None or current_date is None:
        raise KeyError('Ответ API не соответсвует ожидаемому')
    if not isinstance(homeworks, list):
        raise TypeError('У списка домашних работ неверный тип данных')
    return homeworks


def parse_status(homework):
    """Парсинг статуса работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None:
        raise KeyError('В ответе API нет названия работы')
    if homework_status not in HOMEWORK_VERDICTS:
        raise UnknowStatusHomework()

    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    try:
        check_tokens()
    except Exception as error:
        message = error
        logging.critical(message)
        sys.exit('Бот остановлен!')

    # Создаем объект класса бота
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
