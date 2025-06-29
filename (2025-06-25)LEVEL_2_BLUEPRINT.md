## Phase 1: mkmk_help.py 改修

- 現在
    - mkmk.csv へ出力して終了している
- こうする
    - csv へ出力して終了する
    - 新たに `csv_to_xlsx.py` を作成して、 csv から xlsx へ変換する

```bash
# こういうふうになる
pipenv run python mkmk_help.py --base-url https://WWW.JAV.OR.JP --total-row 1
pipenv run python csv_to_xlsx.py --csv ./mkmk.csv --xlsx ./mkmk.xlsx
```

ただ、 xlsx をこの段階で作る予定はなくて、わざわざ csv に出力するのは、以下の `mkmk_help_2.py` で読み込み直すため。

### 実際の改修内容 (完了)

上述のものに加えて……

- jb から取得するデータは、改行を削除して保存 (CSV を経由するから、少しでもデータをシンプルにしておきたい)
- organization データの構築を mkmk_help から jb へ移動 (どう考えてもこっちやろ)

## Phase 2: mkmk_help_2.py 新規作成

- csv を取得する

```bash
pipenv run python mkmk_help_2.py --csv ./mkmk.csv
```

- name, location, url 列を取得する
- 検索ワード (次項で使う) を作成する: name を正規化処理する
    - 正規化ロジック (関数で切り替え可能)
        - v1: スペースをすべて削除
        - v2: 株式会社、有限会社、合同会社などの法人格除去 + スペース削除
        - v3: 法人格除去 + 全角英数字→半角統一 + スペース・記号正規化
- `jn_search_url` を作成する
- beautiful soup で `jn_search_url` を取得する
- html から検索結果一覧を取得する
- 検索一覧の中で、探しているものを探す
    - マッチングロジック (関数で切り替え可能)
        - v1: 完全一致 - csv から取得した location と、住所が完全一致する検索結果
        - v2: 部分一致 - 住所の一部が一致する検索結果
        - v3: 正規化後一致 - 都道府県、市区町村レベルで段階的にマッチング
- 探した結果……
    - 見つかった -> 検索結果の中から電話番号 (tel) と詳細 URL (jn_detail_url) を取得
    - 見つからない -> 空文字列でいい
- こういうデータができる
    - name, location, jb_url (もともとの csv の url), tel, jn_search_url, jn_detail_url
- このデータを csv へ出力する
