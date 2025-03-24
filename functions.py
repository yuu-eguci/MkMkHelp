import json
import sys
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def fetch_rendered_html(url: str) -> str:
    options = Options()
    options.add_argument("--headless")
    print("<SYS> options 準備おｋ")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    print("<SYS> driver.get おｋ")

    # AJAX を待つタイム。これをやりたいから bs4 ではなく、selenium を使っている。
    time.sleep(3)
    print("<SYS> sleep おｋ")

    html = driver.page_source
    print("<SYS> page_source おｋ")

    driver.quit()
    print("<SYS> quit おｋ")
    return html


def extract_organization_list(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    result = []
    rows = soup.find_all("tr", class_="ant-table-row ant-table-row-level-0")

    for row in rows:
        link = row.find("a", class_="app-link")
        if link and link.text and link.get("href"):
            result.append({"name": link.get_text(strip=True), "path": link["href"]})

    return result


def save_to_excel(data: list[dict[str, str]], filename: str) -> None:
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)


def fetch_html(url: str) -> str:
    """指定された URL の HTML を取得して構造を表示する"""
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.prettify()


def extract_next_data_json(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if script_tag:
        try:
            return json.loads(script_tag.string)
        except json.JSONDecodeError:
            print("JSON デコードに失敗しちゃった…")
    return {}


def print_progress(current: int, total: int, name: str) -> None:
    message = f"{current}（{name}）/{total} おわり"
    sys.stdout.write("\r" + " " * 100 + "\r")
    sys.stdout.write(message)
    sys.stdout.flush()
