import argparse
import logging

import pandas as pd

import jn
import shared

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

    # TODO: 以降の処理を実装予定

    logger.info("end mkmk_help_3")


if __name__ == "__main__":
    main()
