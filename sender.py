import datetime
from selenium.common import InvalidSessionIdException

from config import CHANNELS, TARGET_CHAT
from db import get_last_post_time, update_last_post_time
from parser import *
from session import *
from filter import *
from OpenAI_handler import *


def extract_first_datetime(date_str):
    pattern = r"(\d{1,2}\s+[A-Za-z]+\s+\d{4},\s+\d{2}:\d{2}:\d{2})"
    match = re.search(pattern, date_str)
    if match:
        return match.group(1)
    return None


def compare_date_strings(db_date, message_date):
    date_format = "%d %B %Y, %H:%M:%S"
    db_date_extracted = db_date
    message_date_extracted = extract_first_datetime(message_date)

    if db_date_extracted is None or message_date_extracted is None:
        raise ValueError("Не удалось извлечь дату из одной из строк.")

    db_dt = datetime.datetime.strptime(db_date_extracted, date_format)
    message_dt = datetime.datetime.strptime(message_date_extracted, date_format)

    return db_dt < message_dt


def handle_new_message(app, elem, channel):
    try:
        db_time = get_last_post_time(channel)
        message_time = elem.get("time")
        if message_time is None:
            print("В сообщении отсутствует время, пропускаем его.")
            return

        if db_time is not None:
            if compare_date_strings(db_time, message_time):
                update_last_post_time(channel, extract_first_datetime(message_time))
            else:
                print(f"{db_time} -- {message_time} -- Сообщение старое, пропускаем его.")
                return
        else:
            update_last_post_time(channel, extract_first_datetime(message_time))
    except Exception as e:
        print(f"Ошибка при проверке времени: {e}")
        return

    try:
        anchor_url = elem.get("anchor_url")
        if is_source_on_hh_ru(anchor_url):
            target_channel = TARGET_CHAT if TARGET_CHAT.startswith('@') else f"@{TARGET_CHAT}"
            app.send_message(target_channel, f"Вакансия на HeadHunter \n{anchor_url}")
            logger.info(f"Сообщение из канала {channel} переслано в {target_channel}.")
            return
    except Exception as e:
        print(f"Нет anchor_url в посте {e}")


    try:
        message_text = elem.get("text", "")
        if not is_relevant(message_text):
            print("Сообщение не соответствует критериям фильтрации.")
            return

        openai_response = check_with_openai(message_text)
        if not openai_response or not openai_response.get("approve"):
            print("Сообщение не прошло проверку через OpenAI.")
            return

        target_channel = TARGET_CHAT if TARGET_CHAT.startswith('@') else f"@{TARGET_CHAT}"
        app.send_message(target_channel, openai_response.get("formalization"))
        logger.info(f"Сообщение из канала {channel} переслано в {target_channel}.")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        return


def start_parsing(app):
    current_driver = get_driver()
    manual_login(current_driver)

    while True:
        html_counter = 1
        span_counter = 1
        try:
            for channel in CHANNELS:
                current_url = f"https://web.telegram.org/k/#@{channel}"
                print(f"Обрабатывается канал {channel}")
                open_channel(current_driver, current_url, channel)
                current_html = parse_html(current_driver, html_counter)
                current_posts = extract_translatable_spans(current_html, span_counter)
                html_counter += 1
                span_counter += 1

                print(f"Найдено {len(current_posts)} постов")
                for elem in current_posts:
                    handle_new_message(app, elem, channel)
        except InvalidSessionIdException as e:
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Ошибка: недействительная сессия обнаружена. Перезапускаем драйвер...")
            try:
                current_driver.quit()
            except Exception as ex:
                print("Ошибка при закрытии драйвера:", ex)
            current_driver = get_driver()
            manual_login(current_driver)
            continue
        except Exception as e:
            print("Произошла непредвиденная ошибка:", e)

        try:
            current_driver.execute_cdp_cmd("Network.clearBrowserCache", {})
            print("Кэш браузера очищен.")
        except Exception as e:
            print("Ошибка при очистке кэша браузера:", e)

        print("Ожидание 1 минуту...")
        time.sleep(60)


if __name__ == "__main__":
    app = get_session()
    start_session(app)
    start_parsing(app)
    app.stop()
