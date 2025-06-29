import argparse
import logging

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main() -> None:
    logger.info("start csv_to_xlsx")

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Input CSV file path")
    parser.add_argument("--xlsx", required=True, help="Output XLSX file path")
    args = parser.parse_args()

    csv_path = args.csv
    xlsx_path = args.xlsx

    # CSV を読み込み
    # dtype=str を指定して、すべての列を文字列型として読み込む。
    df = pd.read_csv(csv_path, encoding="utf-8", dtype=str)
    logger.info(f"{csv_path} を文字列型で読み込み完了")

    # 出力順とヘッダー対応表。
    column_map = {
        "name": "name(jbサイトでの名前)",
        "location": "location(jbサイトに載ってる住所)",
        "url": "url(jbサイトの詳細ページ)",
        "jn_tel": "jn_tel(これじゃね？っていう電話番号)",
        "jn_tel_hyphen": "jn_tel_hyphen(ハイフンつき)",
        "jn_search_url": "jn_search_url(jnサイトをこのURLで検索したよ)",
        "jn_company_name": "jn_company_name(jnサイトでの名前)",
        "jn_location": "jn_location(jnサイトに載ってる住所)",
        "jn_detail_url": "jn_detail_url(jnサイトの詳細ページ)",
        "jn_memo": "jn_memo(jnの処理におけるコメント)",
    }

    # 存在する列だけを順序付きで選択し、ヘッダーを書き換え。
    selected_columns = [col for col in column_map.keys() if col in df.columns]
    df_selected = df[selected_columns].rename(columns={c: column_map[c] for c in selected_columns})

    # XLSX として保存
    df_selected.to_excel(xlsx_path, index=False)
    logger.info(f"{xlsx_path} に保存完了 (ヘッダー書き換え＆順序指定)")

    logger.info("end csv_to_xlsx")


if __name__ == "__main__":
    main()
