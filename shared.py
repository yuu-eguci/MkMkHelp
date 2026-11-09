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

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/91.0.4472.124 Safari/537.36"
)


def fetch_html_slowly(url: str, wait_sec: int = 3) -> str:
    """
    指定された URL にアクセスし、JavaScript 実行後の HTML をのんびり取得します。
    Cloudflare の bot 検出を回避するための設定を追加。
    """

    options = Options()
    # ヘッドレスモード (見えるウィンドウを出さずに裏でウィンドウを動かすこと) を有効化
    options.add_argument("--headless")
    # Cloudflare 回避のための設定
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    # User-Agent を設定
    options.add_argument(f"--user-agent={USER_AGENT}")
    logger.info("options 準備おｋ")

    driver = webdriver.Chrome(options=options)
    # NOTE: 例外が出ても Chrome を残さないよう、必ず quit する。
    try:
        # WebDriver の自動化検出を無効化
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        driver.get(url)
        logger.info("driver.get おｋ")

        # Cloudflare チャレンジページかどうかをチェック。
        if "Just a moment..." in driver.page_source or "Verify you are human" in driver.page_source:
            logger.info("Cloudflare チャレンジページを検出、待機中...")
            # より長い時間待機してチャレンジの完了を待つ
            max_wait = 30  # 最大30秒待機
            for i in range(max_wait):
                time.sleep(1)
                if "Just a moment..." not in driver.page_source and "Verify you are human" not in driver.page_source:
                    logger.info(f"Cloudflare チャレンジ完了 ({i + 1}秒後)")
                    break
                if i == max_wait - 1:
                    logger.warning("Cloudflare チャレンジのタイムアウト")

        # 通常の待機時間
        time.sleep(wait_sec)
        logger.info("sleep おｋ")

        html = driver.page_source
        logger.info("page_source おｋ")
    finally:
        driver.quit()
    logger.info("driver.quit おｋ")
    return html


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


def show_progress_with_name(current: int, total: int, name: str) -> None:
    """
    処理の進捗を、ガンガン上書き表示します。
    """
    message = f"{current}（{name}）/{total} おわり"
    sys.stdout.write("\r" + " " * 100 + "\r")
    sys.stdout.write(message)
    sys.stdout.flush()
