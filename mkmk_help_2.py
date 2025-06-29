import argparse
import logging
from time import sleep

import pandas as pd

import jn
import shared

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main() -> None:
    logger.info("start mkmk_help_2")

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Input CSV path")
    parser.add_argument("--jn-base-url", required=True, help="Base URL for jn search")
    parser.add_argument("--output-csv", default="mkmk.csv", help="Output CSV file path (UTF-8 with BOM) ")
    args = parser.parse_args()
    base_url = args.jn_base_url
    output_csv = args.output_csv

    # CSV を読み込みます。
    df = pd.read_csv(args.csv)
    logger.info(f"CSV 読み込みおｋ: {args.csv}")

    # 必要な列だけ抽出します。
    try:
        df_sub = df[["name", "location", "url"]].copy()
        logger.info("name, location, url 列の抽出おｋ")
    except KeyError as e:
        logger.error(f"必要な列が見つかりません: {e}")
        return

    # 検索ワード (次項で使う) を作成します。
    # NOTE: いまのところ、スペース除去のみがもっとも適切そう。
    df_sub["name_no_space"] = df_sub["name"].apply(jn.remove_spaces)

    # 検索 URL の列を追加 (ここでは name_no_space を使う例)
    df_sub["jn_search_url"] = df_sub["name_no_space"].apply(lambda x: jn.create_search_url(base_url, x))

    # この状態で csv に保存する。
    df_sub.to_csv("mkmk_help_2_jn_search_url.csv", index=False, encoding="utf_8_sig")

    # 空列を最初に作る
    df_sub["jn_tel"] = ""
    df_sub["jn_tel_hyphen"] = ""
    df_sub["jn_company_name"] = ""
    df_sub["jn_location"] = ""
    df_sub["jn_detail_url"] = ""
    df_sub["jn_memo"] = ""

    for idx, row in df_sub.iterrows():
        test_url = row["jn_search_url"]
        test_location = row["location"]

        try:
            # HTML を取得します。
            html = shared.fetch_html_slowly(test_url, wait_sec=10)
            # NOTE: 連続アクセスをやめようか。
            sleep(0.5)

            # デバッグ用に HTML をファイルに保存します。
            # debug_filename = "debug_output.html"
            # with open(debug_filename, "w", encoding="utf-8") as f:
            #     f.write(html)
            # logger.info(f"デバッグ用 HTML を保存: {debug_filename}")

            # HTML から検索結果の一覧を取得する
            search_results = jn.parse_search_results(html)

            logger.info(f"[{idx}] 検索結果の取得おｋ: {len(search_results)} 件")

            # 一覧の中から、もっとも適切っぽいものを選ぶ。
            # "もっとも適切っぽい":
            #     csv から取得した住所と、 html から取得した住所 -> 正規化 -> 比較
            best_match = jn.find_best_match(search_results, test_location)

            # それを csv へ!
            if best_match:
                logger.info(f"[{idx}] 最適な一致を見つけた: {best_match}")

                tel_raw = best_match.get("tel", "")
                tel_no_hyphen, tel_hyphen = jn.split_tel_field(tel_raw)

                df_sub.at[idx, "jn_tel"] = tel_no_hyphen
                df_sub.at[idx, "jn_tel_hyphen"] = tel_hyphen
                df_sub.at[idx, "jn_company_name"] = best_match.get("company_name", "")
                df_sub.at[idx, "jn_location"] = best_match.get("location", "")
                df_sub.at[idx, "jn_detail_url"] = base_url + "/" + best_match.get("detail_url", "")
            else:
                logger.warning(f"[{idx}] 最適な一致が見つからなかった。")
                df_sub.at[idx, "jn_memo"] = "なんかこれは見つからなかったわ。検索 URL つけたからそれ見てみて。"

            # NOTE: 無効なときがたくさんあるから、処理ごとに保存することにした。
            df_sub.to_csv(output_csv, index=False, encoding="utf_8_sig")
        except Exception as e:
            df_sub.at[idx, "jn_memo"] = f"なんかエラー起きたわ: {str(e)}"
            logger.error(f"[{idx}] 処理中にエラー: {e}")

        # 進捗を表示。
        shared.show_progress_with_name(idx + 1, len(df_sub), row["name"])

    logger.info("end mkmk_help_2")


if __name__ == "__main__":
    main()
