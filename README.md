MkMkHelp
===

![](./doc/readme.png)

ﾐｶﾐｶﾍﾙﾌﾟ!

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

# mkmk_help total_row を編集。

# LEVEL1 実行。本物の URL の掲載を避けています。 URL は適切に変えること。
time pipenv run python mkmk_help.py --base-url https://WWW.JAV.OR.JP --total-row 1 --output-csv mkmk_help_1.csv

# LEVEL2 実行。
time pipenv run python mkmk_help_2.py --jn-base-url https://WWW.JN.COM --csv mkmk_help_1.csv --output-csv mkmk_help_2.csv

# 必要に応じて csv を xlsx に変換
pipenv run python csv_to_xlsx.py --csv ./mkmk_help_2.csv --xlsx ./mkmk.xlsx

# 便利機能
pipenv run python xlsx_to_csv.py --xlsx ./mkmk.xlsx --csv ./mkmk.csv
```

## Room for improvement

- ロギングが複数行に渡るときがあるから、 organization name は最初の数文字だけでいいかも
- for の最中にエラーになるとパァだから、 csv に append していくか try - except - finally がいいかも
