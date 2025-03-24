import logging
import sys
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def fetch_html_slowly(url: str, wait_sec: int = 3) -> str:
    """
    指定された URL にアクセスし、JavaScript 実行後の HTML をのんびり取得します。
    """

    options = Options()
    options.add_argument("--headless")
    logger.info("options 準備おｋ")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    logger.info("driver.get おｋ")

    # AJAX を待つタイム。これをやりたいから bs4 ではなく、selenium を使っている。
    time.sleep(wait_sec)
    logger.info("sleep おｋ")

    html = driver.page_source
    logger.info("page_source おｋ")

    driver.quit()
    logger.info("driver.quit おｋ")
    return html


def save_to_xlsx(data: list[dict[str, str]], filename: str) -> None:
    """
    辞書のリストを xlsx ファイルとして保存します。
    """

    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    logger.info(f"{filename} おｋ")


def fetch_html(url: str) -> str:
    """
    指定された URL の HTML を取得して構造を表示する
    """

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.prettify()


def show_progress_with_name(current: int, total: int, name: str) -> None:
    """
    処理の進捗を、ガンガン上書き表示します。
    """
    message = f"{current}（{name}）/{total} おわり"
    sys.stdout.write("\r" + " " * 100 + "\r")
    sys.stdout.write(message)
    sys.stdout.flush()
