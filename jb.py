import json
import logging

from bs4 import BeautifulSoup

from shared import normalize_csv_data

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def extract_organizations_from_html(html: str) -> list[dict[str, str]]:
    """
    指定された HTML から、組織名と詳細ページパスを抽出します。
    [{name, path}, ...]
    """
    soup = BeautifulSoup(html, "html.parser")
    result = []
    rows = soup.find_all("tr", class_="ant-table-row ant-table-row-level-0")

    for row in rows:
        link = row.find("a", class_="app-link")
        if link and link.text and link.get("href"):
            result.append({"name": link.get_text(strip=True), "path": link["href"]})

    return result


def extract_next_data_from_html(html: str) -> dict:
    """
    指定された HTML から、<script id="__NEXT_DATA__"> に埋め込まれた JSON を抽出する。
    """
    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if script_tag:
        try:
            return json.loads(script_tag.string)
        except json.JSONDecodeError:
            logger.error("JSON デコードに失敗しちゃった…")
            raise
    return {}


def build_organization_data(name: str, location: str, url: str) -> dict[str, str]:
    """
    組織データを構築し、CSV 用に正規化します。
    normalize_csv_data で改行を半角スペースに変換する。
    NOTE: まあ、改行が入っているとこのあと扱いづらくなるなあ、と思ったので。
    """
    return {
        "name": normalize_csv_data(name),
        "location": normalize_csv_data(location),
        "url": url,
    }
