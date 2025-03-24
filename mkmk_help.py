import argparse
import logging
from time import sleep

from jab import extract_next_data_from_html, extract_organizations_from_html
from shared import (
    fetch_html,
    fetch_html_slowly,
    save_to_xlsx,
    show_progress_with_name,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main() -> None:
    logger.info("start mkmk_help")

    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="", help="Base url")
    args = parser.parse_args()
    base_url = args.base_url

    # メッチャおもろいんだけど一度の表示件数をコッチで決めれるｗ
    total_row = 5
    list_url = f"{base_url}/compatible_organizations?page=1&standards=140012015&pageSize={total_row}&nationality=JPN&classification=28" # noqa: E501

    # html ゲット。
    html: str = fetch_html_slowly(list_url, wait_sec=3)

    # 会社名と、リンクをゲット。
    organizations: list[dict[str, str]] = extract_organizations_from_html(html)

    for i, org in enumerate(organizations):
        # 1社ずつ詳細画面にアクセス。
        detail_url = f"{base_url}{org['path']}"
        # print(detail_url)
        detail_html: str = fetch_html(detail_url)
        # print(detail_html)
        detail_json: dict = extract_next_data_from_html(detail_html)
        # print(detail_json)
        org["regis_num"] = detail_json["props"]["pageProps"]["organization"]["attributes"]["regis_num"]
        del org["path"]
        show_progress_with_name(i + 1, len(organizations), org["name"])
        # NOTE: 連続アクセスをやめようか。
        sleep(0.5)

    # NOTE: 改行のため
    print()

    save_to_xlsx(organizations, "mkmk.xlsx")

    logger.info("end mkmk_help")


if __name__ == "__main__":
    main()
