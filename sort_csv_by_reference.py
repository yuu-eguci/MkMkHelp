"""
pipenv run python sort_csv_by_reference.py --reference-csv reference.csv --target-csv target.csv --output-csv output.csv
"""

import argparse
import logging

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")


def main() -> None:
    logger.info("start sort_csv_by_reference")

    parser = argparse.ArgumentParser(description="CSV ファイルを参照ファイルの URL 順序に従って並び替える")
    parser.add_argument("--reference-csv", required=True, help="参照順序の CSV ファイルパス")
    parser.add_argument("--target-csv", required=True, help="並び替え対象の CSV ファイルパス")
    parser.add_argument("--output-csv", required=True, help="出力 CSV ファイルパス")
    args = parser.parse_args()

    reference_csv = args.reference_csv
    target_csv = args.target_csv
    output_csv = args.output_csv

    logger.info(f"設定: 参照CSV={reference_csv}, 対象CSV={target_csv}, 出力CSV={output_csv}")

    try:
        # CSV ファイルを読み込み
        logger.info(f"参照ファイルを読み込み中: {reference_csv}")
        reference_df = pd.read_csv(reference_csv)
        logger.info(f"参照ファイル読み込みおｋ: {len(reference_df)} 行")

        logger.info(f"対象ファイルを読み込み中: {target_csv}")
        target_df = pd.read_csv(target_csv)
        logger.info(f"対象ファイル読み込みおｋ: {len(target_df)} 行")

        # url カラムの存在チェック
        if "url" not in reference_df.columns:
            logger.error("参照ファイルに 'url' カラムがありません")
            return

        if "url" not in target_df.columns:
            logger.error("対象ファイルに 'url' カラムがありません")
            return

        # 並び替え処理
        logger.info("並び替え処理を開始...")
        sorted_df = sort_by_reference_urls(reference_df, target_df)
        logger.info(f"並び替え処理おｋ: {len(sorted_df)} 行")

        # 結果を出力
        logger.info(f"結果を出力中: {output_csv}")
        sorted_df.to_csv(output_csv, index=False, encoding="utf_8_sig")
        logger.info(f"出力おｋ: {output_csv}")

        # 統計情報を表示
        print_statistics(reference_df, target_df, sorted_df)

        logger.info("end sort_csv_by_reference")

    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        raise


def sort_by_reference_urls(reference_df, target_df):
    """
    参照ファイルの URL 順序に従って対象ファイルを並び替える

    Args:
        reference_df: 参照ファイルの DataFrame
        target_df: 対象ファイルの DataFrame

    Returns:
        並び替えられた DataFrame
    """
    logger.info("URL でのマッチング処理を開始")

    # 対象ファイルを URL でインデックス化
    target_indexed = target_df.set_index("url")

    # 並び替え結果を格納するリスト
    sorted_rows = []
    matched_urls = set()

    # 参照ファイルの URL 順序に従って並び替え
    for idx, url in enumerate(reference_df["url"]):
        if url in target_indexed.index:
            # マッチした行を追加
            row = target_indexed.loc[url]
            if isinstance(row, pd.Series):
                # 単一行の場合
                row_dict = row.to_dict()
                row_dict["url"] = url
                sorted_rows.append(row_dict)
                logger.debug(f"[{idx}] マッチ: {url}")
            else:
                # 複数行の場合 (重複 URL)
                for _, r in row.iterrows():
                    row_dict = r.to_dict()
                    row_dict["url"] = url
                    sorted_rows.append(row_dict)
                logger.debug(f"[{idx}] マッチ (複数): {url}")
            matched_urls.add(url)
        else:
            logger.debug(f"[{idx}] 対象ファイルに見つからない: {url}")

    # 参照ファイルにない URL の行を最後に追加
    unmatched_rows = target_df[~target_df["url"].isin(matched_urls)]
    for _, row in unmatched_rows.iterrows():
        sorted_rows.append(row.to_dict())
        logger.debug(f"参照ファイルにない URL を最後に追加: {row['url']}")

    # DataFrame に変換
    if sorted_rows:
        sorted_df = pd.DataFrame(sorted_rows)
        # 元の列順序を保持
        sorted_df = sorted_df[target_df.columns]
    else:
        # 空の場合は元の構造を保持
        sorted_df = pd.DataFrame(columns=target_df.columns)

    logger.info("URL マッチング処理おｋ")
    return sorted_df


def print_statistics(reference_df, target_df, sorted_df):
    """
    処理統計を表示する
    """
    logger.info("=== 処理統計 ===")
    logger.info(f"参照ファイル行数: {len(reference_df)}")
    logger.info(f"対象ファイル行数: {len(target_df)}")
    logger.info(f"出力ファイル行数: {len(sorted_df)}")

    # マッチング統計
    reference_urls = set(reference_df["url"])
    target_urls = set(target_df["url"])
    matched_urls = reference_urls & target_urls

    logger.info(f"マッチした URL 数: {len(matched_urls)}")
    logger.info(f"参照ファイルにのみ存在する URL 数: {len(reference_urls - target_urls)}")
    logger.info(f"対象ファイルにのみ存在する URL 数: {len(target_urls - reference_urls)}")


if __name__ == "__main__":
    main()
