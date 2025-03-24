MkMkHelp
===

![](./doc/readme.png)

ﾐｶﾐｶﾍﾙﾌﾟ!

## Install

```bash
# pipenv + Python 3.10 ある前提
pipenv sync

# mkmk_help total_row を編集。

# 実行。本物の URL の掲載を避けています。 URL は適切に変えること。
time pipenv run python mkmk_help.py --base-url https://WWW.JAV.OR.JP --total-row 1
```

## Room for improvement

- ロギングが複数行に渡るときがあるから、 organization name は最初の数文字だけでいいかも
- for の最中にエラーになるとパァだから、 csv に append していくか try - except - finally がいいかも
