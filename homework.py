import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    filename='homework.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# проинициализируйте бота здесь,
# чтобы он был доступен в каждом нижеобъявленном методе,
# и не нужно было прокидывать его в каждый вызов
bot = telegram.Bot(token=TELEGRAM_TOKEN)
logging.debug('Start the Telegram bot')


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework.get('status') != 'approved':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    elif homework.get('status') is None or homework_name is None:
        logging.error('Неверный ответ сервера')
        return 'Неверный ответ сервера'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    if current_timestamp is None:
        current_timestamp = int(time.time())
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
        return homework_statuses.json()

    except requests.exceptions.Timeout:
        err_message = 'Ошибка получения ответа Timeout'
        logging.error(err_message)
        send_message(err_message)
        print(err_message)
        time.sleep(5)

    except requests.exceptions.HTTPError as e:
        err_message = f'Ошибка получения ответа HTTP: {e}'
        logging.error(err_message)
        send_message(err_message)
        print(err_message)
        time.sleep(5)

    except requests.exceptions.RequestException as e:
        err_message = f'Ошибка запроса к API: {e}'
        logging.error(err_message)
        send_message(err_message)
        print(err_message)
        time.sleep(5)


def send_message(message):
    logging.info(f'Send a message: {message}')
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp

    while True:
        try:
            req_timestamp = current_timestamp - (5 * 60 + 5)
            homeworks = get_homeworks(req_timestamp)['homeworks']
            for homework in homeworks:
                message = parse_homework_status(homework)
                send_message(message)

            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            err_message = f'Бот упал с ошибкой: {e}'
            logging.error(err_message)
            send_message(err_message)
            print(err_message)
            time.sleep(5)


if __name__ == '__main__':
    main()
