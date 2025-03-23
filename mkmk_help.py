from time import sleep

from functions import extract_next_data_json, extract_organization_list, fetch_html, fetch_rendered_html, save_to_excel


def main() -> None:
    # メッチャおもろいんだけど一度の表示件数をコッチで決めれるｗ
    total_row = 3055
    list_url = f"https://www.jab.or.jp/compatible_organizations?page=1&standards=140012015&pageSize={total_row}&nationality=JPN&classification=28"

    # html ゲット。
    html: str = fetch_rendered_html(list_url)

    # 会社名と、リンクをゲット。
    organizations: list[dict[str, str]] = extract_organization_list(html)

    for i, org in enumerate(organizations):
        # 1社ずつ詳細画面にアクセス。
        detail_url = f"https://www.jab.or.jp{org['path']}"
        # print(detail_url)
        detail_html: str = fetch_html(detail_url)
        # print(detail_html)
        detail_json: dict = extract_next_data_json(detail_html)
        # print(detail_json)
        org["regis_num"] = detail_json["props"]["pageProps"]["organization"]["attributes"]["regis_num"]
        del org["path"]
        print(f"\r{i + 1}（{org['name']}）/{len(organizations)} おわり", end="", flush=True)
        # NOTE: 連続アクセスをやめようか。
        sleep(0.5)

    # NOTE: 改行のため
    print()

    save_to_excel(organizations, "mkmk.xlsx")


if __name__ == "__main__":
    main()
