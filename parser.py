import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Для сервера на деплое
# def get_driver():
#     options = Options()
#
#     project_root = os.path.abspath(os.path.dirname(__file__))
#     profile_path = os.path.join(project_root, "ChromeProfile")
#     options.add_argument(f"user-data-dir={profile_path}")
#
#     profile_path = os.getenv("CHROME_PROFILE")
#     if profile_path:
#         options.add_argument(f"--user-data-dir={profile_path}")
#
#     options.add_argument('--headless')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     driver = webdriver.Chrome(options=options)
#     return driver

# Для локалки
def get_driver():
    options = Options()
    options.add_argument("user-data-dir=C:/Selenium/ChromeProfile")
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    return driver


def manual_login(driver):
    driver.get("https://web.telegram.org/")
    print("🔵 Пожалуйста, войдите в Telegram Web вручную, затем нажмите Enter...")
    # input("✅ Нажмите Enter после входа...")


def open_channel(driver, url, channel):
    driver.refresh()
    driver.get(url)
    if channel == "archi_ru":
        time.sleep(60)
    else:
        time.sleep(30)


def scroll_down(driver, scroll_times=5):
    chat_container = driver.find_element(By.TAG_NAME, "body")
    for i in range(scroll_times):
        print(f"🔽 Прокрутка {i + 1}...")
        chat_container.send_keys(Keys.PAGE_UP)
        time.sleep(2)


def parse_html(driver, html_counter):
    html = driver.page_source
    with open(f"htmls/full_page{html_counter}.html", "w", encoding="utf-8") as file:
        file.write(html)
    print("✅ Полный HTML сохранен в 'full_page.html'")
    return html


def extract_translatable_spans(html, span_counter):
    soup = BeautifulSoup(html, 'html.parser')
    span_elements = soup.find_all("span", class_="translatable-message")

    result = []

    with open(f"spans/spans{span_counter}.txt", "w", encoding="utf-8") as file:
        for span in span_elements:
            try:
                text = span.get_text(strip=True)
            except Exception as e:
                print("Наден пост без текста")

            time_div = span.find_next_sibling("div", class_="time-inner")
            if not time_div:
                time_div = span.parent.find("div", class_="time-inner")
            post_time = time_div.get("title") if time_div else None

            try:
                anchor = span.find("a", class_="anchor-url")
            except Exception as e:
                pass
            anchor_url = anchor.get("href") if anchor else None

            post_data = {"text": text, "time": post_time, "anchor_url": str(anchor_url)}
            result.append(post_data)
            file.write("Text: " + text + "\n")
            file.write("Time: " + (post_time if post_time else "None") + "\n")
            file.write("Anchor_url:" + (anchor_url if anchor_url is not None else "There's not any anchor_url") + "\n")
            file.write("\n" + "=" * 40 + "\n\n")

    print("✅ Содержимое всех span с классом 'translatable-message' сохранено в 'spans.txt'")
    return result

# if __name__ == "__main__":
    # driver = get_driver()
    # manual_login(driver)
    #
    # url = "https://web.telegram.org/k/#@nevolk_vacancies"
    # open_channel(driver, url)
    #
    # html = parse_html(driver)
    # posts = extract_posts_from_html(html)
    # extract_translatable_spans(html)
    #
    # driver.quit()


