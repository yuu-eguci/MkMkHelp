MkMkHelp
===

![](./doc/readme.png)

ﾐｶﾐｶﾍﾙﾌﾟ!

jb サイトの組織一覧から組織名と住所を集め、jn サイトで電話番号を探して CSV にまとめるスクリプト集。
本物の URL は掲載していない。 `--base-url` / `--jn-base-url` には適切な URL を指定すること。

## パイプライン

| スクリプト | 入力 | やること | 出力 |
| --- | --- | --- | --- |
| `mkmk_help.py` (Level 1) | jb サイト | 組織一覧と各詳細ページから `name`, `location`, `url` を取得する。改行や連続空白は半角スペース 1 つにまとめる。 | CSV (UTF-8) |
| `mkmk_help_2.py` (Level 2) | Level 1 の CSV | 名前で jn サイトを検索し、住所がもっとも近い結果の電話番号を採用する。 | CSV (UTF-8 BOM) |
| `mkmk_help_3.py` (Level 3) | Level 2 の CSV | 住所で jn サイトを検索し、名前がもっとも近い結果の電話番号を採用する。 | CSV (UTF-8 BOM) |
| `csv_to_xlsx.py` | CSV | 主要な列だけを決まった順に選び、説明つきヘッダーにして xlsx にする。 | xlsx |
| `xlsx_to_csv.py` | xlsx | xlsx を CSV に戻す。 | CSV (UTF-8) |
| `sort_csv_by_reference.py` | CSV 2 つ | 対象 CSV を参照 CSV の `url` 順に並べ替える。参照にない行は末尾に残す。 | CSV (UTF-8 BOM) |

Level 2 / Level 3 が追加する列:

- `jn_search_url`: jn サイトの検索 URL
- `jn_tel`, `jn_tel_hyphen`: 採用した電話番号 (ハイフンなし / あり)
- `jn_company_name`, `jn_location`, `jn_detail_url`: 採用した検索結果の名前、住所、詳細ページ
- `jn_memo`: 見つからなかった、アクセスを拒否された (401)、エラーになった、などのメモ

Level 2 は検索語として `name_no_space` 列も追加し、検索 URL だけを入れた中間ファイル `mkmk_help_2_jn_search_url.csv` も出力する。
Level 3 は検索語として `location_no_space` 列を追加する。

### マッチング方針

- Level 2 (住所で照合): 郵便番号、空白、`番地` / `丁目` / `号` / ハイフンを除去し、漢数字・全角数字を半角数字にそろえ、市の中の区を省いて比較する。
  完全一致 1.0、都道府県が違えば 0.0、市区町村まで一致すれば残りの先頭一致率に応じて 0.6〜1.0、都道府県だけ一致なら 0.3。
  0.7 以上でもっとも高い結果を採用する。
- Level 3 (名前で照合): 法人格 (株式会社 / 有限会社 / 合同会社)、記号、空白を除去し、全角英数字を半角・小文字にそろえて比較する。
  完全一致 1.0、一方がもう一方を含む場合は「短い方の長さ / 長い方の長さ」。
  0.7 以上でもっとも高い結果を採用する。

## Install

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = "Tls12"
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

choco install python --version=3.10 -y

choco install googlechrome --ignore-checksums -y

choco install vscode -y

choco install git -y

# ここで gitbash 開きたい。

git clone https://github.com/yuu-eguci/MkMkHelp.git

pip install pipenv
```

```bash
# pipenv + Python 3.10 ある前提
pipenv sync
```

## Usage

```bash
# Level 1: --total-row は一覧で一度に取得する件数。
time pipenv run python mkmk_help.py --base-url https://WWW.JAV.OR.JP --total-row 1 --output-csv mkmk_help_1.csv

# Level 2
time pipenv run python mkmk_help_2.py --jn-base-url https://WWW.JN.COM --csv mkmk_help_1.csv --output-csv mkmk_help_2.csv

# Level 3: --wait-sec はページ読み込み後の待機秒数 (デフォルト 10)。
time pipenv run python mkmk_help_3.py --jn-base-url https://WWW.JN.COM --csv mkmk_help_2.csv --output-csv mkmk_help_3.csv

# 必要に応じて csv を xlsx に変換
pipenv run python csv_to_xlsx.py --csv ./mkmk_help_3.csv --xlsx ./mkmk.xlsx

# 便利機能
pipenv run python xlsx_to_csv.py --xlsx ./mkmk.xlsx --csv ./mkmk.csv
pipenv run python sort_csv_by_reference.py --reference-csv mkmk_help_1.csv --target-csv mkmk.csv --output-csv mkmk_sorted.csv
```

## Development

```bash
pipenv sync --dev

# テスト。外部サイトにはアクセスせず、合成データだけを使う。
pipenv run pytest

# lint とフォーマットチェック。
pipenv run ruff check .
pipenv run ruff format --check .
```

GitHub Actions (`.github/workflows/ci.yml`) が push と pull request で同じチェックを実行する。

## Room for improvement

- ロギングが複数行に渡るときがあるから、 organization name は最初の数文字だけでいいかも
- Level 1 は詳細ページの取得中にエラーになると CSV が出力されない
