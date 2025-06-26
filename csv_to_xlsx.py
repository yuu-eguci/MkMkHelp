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
    df = pd.read_csv(csv_path, encoding="utf-8")
    logger.info(f"{csv_path} を読み込み完了")

    # XLSX として保存
    df.to_excel(xlsx_path, index=False)
    logger.info(f"{xlsx_path} に保存完了")

    logger.info("end csv_to_xlsx")


if __name__ == "__main__":
    main()
