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


def save_to_csv(data: list[dict[str, str]], filename: str) -> None:
    """
    辞書のリストを csv ファイルとして保存します。
    """

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding="utf-8")
    logger.info(f"{filename} おｋ")


def normalize_csv_data(text: str) -> str:
    """
    CSV 用にテキストを正規化します。
    改行文字を半角スペースに変換し、連続する空白を単一の空白にします。
    """
    if not text:
        return ""
    # 改行文字を半角スペースに変換 (CRLF を先に処理してから、残りの LF, CR を処理)
    text = text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    # 連続する空白を単一の空白に
    text = " ".join(text.split())
    return text.strip()


def fetch_html(url: str) -> str:
    """
    指定された URL の HTML を取得して構造を表示する
    """

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.prettify()


def fetch_html_with_retry(url: str, max_retries: int = 3, wait_sec: int = 2) -> str:
    """
    リトライ機能付きで HTML を取得し、文字列を返す
    """
    # ブラウザらしいヘッダーを設定 (Accept-Encoding を削除して圧縮を無効化)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",  # noqa: E501
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # エンコーディングを明示的に設定
            if response.encoding is None or response.encoding == "ISO-8859-1":
                response.encoding = "utf-8"

            return response.text

        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep(wait_sec)
            else:
                raise


def show_progress_with_name(current: int, total: int, name: str) -> None:
    """
    処理の進捗を、ガンガン上書き表示します。
    """
    message = f"{current}（{name}）/{total} おわり"
    sys.stdout.write("\r" + " " * 100 + "\r")
    sys.stdout.write(message)
    sys.stdout.flush()
