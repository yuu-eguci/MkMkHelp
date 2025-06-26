import argparse
import logging

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main() -> None:
    logger.info("start xlsx_to_csv")

    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", required=True, help="Input XLSX file path")
    parser.add_argument("--csv", required=True, help="Output CSV file path")
    args = parser.parse_args()

    xlsx_path = args.xlsx
    csv_path = args.csv

    # XLSX を読み込み
    df = pd.read_excel(xlsx_path)
    logger.info(f"{xlsx_path} を読み込み完了")

    # CSV として保存
    df.to_csv(csv_path, index=False, encoding="utf-8")
    logger.info(f"{csv_path} に保存完了")

    logger.info("end xlsx_to_csv")


if __name__ == "__main__":
    main()
