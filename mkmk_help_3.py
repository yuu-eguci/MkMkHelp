import argparse
import logging

import pandas as pd

import jn
import shared
from name_similarity import find_best_match_by_name

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main() -> None:
    logger.info("start mkmk_help_3")

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Input CSV path")
    parser.add_argument("--jn-base-url", required=True, help="Base URL for jn search")
    parser.add_argument("--output-csv", default="mkmk.csv", help="Output CSV file path (UTF-8 with BOM)")
    parser.add_argument("--wait-sec", type=int, default=10, help="Wait seconds between requests")
    args = parser.parse_args()

    base_url = args.jn_base_url
    output_csv = args.output_csv
    wait_sec = args.wait_sec

    logger.info(f"設定: CSV={args.csv}, Base URL={base_url}, Output={output_csv}, Wait={wait_sec}秒")

    # CSV を読み込みます。
    df = pd.read_csv(args.csv)
    logger.info(f"CSV 読み込みおｋ: {args.csv}")

    # name_no_space の隣に location_no_space を配置
    name_no_space_idx = df.columns.get_loc("name_no_space")
    df.insert(name_no_space_idx + 1, "location_no_space", df["location"].apply(jn.remove_spaces))

    # 検索 URL の列を追加 (ここでは location_no_space を使う)
    df["jn_search_url"] = df["location_no_space"].apply(lambda x: jn.create_search_url(base_url, x))

    logger.info("検索 URL の作成おｋ")

    for idx, row in df.iterrows():
        search_url = row["jn_search_url"]
        test_name = row["name"]

        # すでに電話番号が埋まってたらスキップ (NaN と空文字列以外)
        jn_tel_value = row.get("jn_tel", "")
        if pd.notna(jn_tel_value) and str(jn_tel_value).strip() != "":
            logger.info(f"[{idx}] スキップ (すでに処理済み): {test_name}")
            continue

        try:
            logger.info(f"[{idx}] 処理開始: {test_name}")

            # HTML を取得します。
            html = shared.fetch_html_slowly(search_url, wait_sec=wait_sec)

            if "401 Error - Unauthorized Access" in html:
                logger.error(f"[{idx}] アクセスが拒否 (401) されました: {search_url}")
                df.at[idx, "jn_memo"] = "拒否されたわ401。ｱﾁｬｰ!"
                continue

            # HTML から検索結果の一覧を取得する
            search_results = jn.parse_search_results(html)

            logger.info(f"[{idx}] 検索結果の取得おｋ: {len(search_results)} 件")

            # 一覧の中から、もっとも適切っぽいものを選ぶ。
            # Level 3: 住所で検索した結果から、名前でバリデーションする
            best_match = find_best_match_by_name(search_results, test_name)

            # それを csv へ!
            if best_match:
                logger.info(f"[{idx}] 最適な一致を見つけた: {best_match}")

                tel_raw = best_match.get("tel", "")
                tel_no_hyphen, tel_hyphen = jn.split_tel_field(tel_raw)

                df.at[idx, "jn_tel"] = tel_no_hyphen
                df.at[idx, "jn_tel_hyphen"] = tel_hyphen
                df.at[idx, "jn_company_name"] = best_match.get("company_name", "")
                df.at[idx, "jn_location"] = best_match.get("location", "")
                df.at[idx, "jn_detail_url"] = base_url + "/" + best_match.get("detail_url", "")
            else:
                logger.warning(f"[{idx}] 最適な一致が見つからなかった。")
                df.at[idx, "jn_memo"] = "住所検索したけど見つからなかったわ。検索 URL つけたからそれ見てみて。"

        except Exception as e:
            df.at[idx, "jn_memo"] = f"なんかエラー起きたわ: {str(e)}"
            logger.error(f"[{idx}] 処理中にエラー: {e}")
        finally:
            # 毎回保存する
            df.to_csv(output_csv, index=False, encoding="utf_8_sig")

        # 進捗を表示。
        shared.show_progress_with_name(idx + 1, len(df), row["name"])
        # NOTE: 改行。
        print()

    logger.info("end mkmk_help_3")


if __name__ == "__main__":
    main()
