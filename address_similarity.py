import re


def normalize_address(address: str) -> str:
    """
    住所さあ! 書き方いろいろありすぎなんだよ!
    正規化する! (スペース、記号、数字統一)
    """
    if not address:
        return ""

    # 郵便番号を除去。
    # NOTE: csv の住所に郵便番号は無い。
    address = re.sub(r"〒\d{3}-\d{4}\s*", "", address)

    # 漢数字を半角数値に変換。
    # NOTE: ここで住所が誤ることもあるが、これはマッチングのためだけの変換だから問題ない。
    address = _convert_kanji_to_number(address)

    # 全角数字を半角に変換。
    address = address.translate(str.maketrans("０１２３４５６７８９", "0123456789"))

    # スペースたちを除去。
    address = address.replace(" ", "").replace("　", "")

    # 住所表記の統一
    address = address.replace("番地", "")
    address = address.replace("−", "")
    address = address.replace("-", "")
    address = address.replace("丁目", "")
    address = address.replace("号", "")

    # "市の中にある区" を除去。 (例: XX市XX区 → XX市)
    # NOTE: なんかね……区を書かない場合があるようだから。
    address = re.sub(r"(市[^市区町村]{1,10})区", r"\1", address)

    return address


def _convert_kanji_to_number(text: str) -> str:
    """
    漢数字を半角数値に変換する
    """
    if not text:
        return ""

    kanji_map = {
        "一": "1",
        "二": "2",
        "三": "3",
        "四": "4",
        "五": "5",
        "六": "6",
        "七": "7",
        "八": "8",
        "九": "9",
        "十": "10",
    }

    # 基本的な一桁漢数字を変換
    for kanji, digit in kanji_map.items():
        text = text.replace(kanji, digit)

    return text


def calculate_address_similarity(addr1: str, addr2: str) -> float:
    """
    住所の類似度を計算 (0.0-1.0)
    """
    if not addr1 or not addr2:
        return 0.0

    # 正規化
    norm_addr1 = normalize_address(addr1)
    norm_addr2 = normalize_address(addr2)

    # 完全一致
    if norm_addr1 == norm_addr2:
        return 1.0

    # 都道府県の抽出と比較
    prefecture_pattern = r"(北海道|青森県|岩手県|宮城県|秋田県|山形県|福島県|茨城県|栃木県|群馬県|埼玉県|千葉県|東京都|神奈川県|新潟県|富山県|石川県|福井県|山梨県|長野県|岐阜県|静岡県|愛知県|三重県|滋賀県|京都府|大阪府|兵庫県|奈良県|和歌山県|鳥取県|島根県|岡山県|広島県|山口県|徳島県|香川県|愛媛県|高知県|福岡県|佐賀県|長崎県|熊本県|大分県|宮崎県|鹿児島県|沖縄県)"

    pref1 = re.search(prefecture_pattern, norm_addr1)
    pref2 = re.search(prefecture_pattern, norm_addr2)

    # 都道府県が不一致 -> 0.0
    if pref1 and pref2 and pref1.group(1) != pref2.group(1):
        return 0.0

    # 市区町村の抽出と比較
    city_pattern = r"([^都道府県]+?[市区町村])"

    # 都道府県を除去してから市区町村を抽出
    addr1_without_pref = norm_addr1.replace(pref1.group(1), "") if pref1 else norm_addr1
    addr2_without_pref = norm_addr2.replace(pref2.group(1), "") if pref2 else norm_addr2

    city1 = re.search(city_pattern, addr1_without_pref)
    city2 = re.search(city_pattern, addr2_without_pref)

    # 市区町村が一致する場合
    if city1 and city2 and city1.group(1) == city2.group(1):
        # 残りの部分の類似度を計算
        remaining1 = addr1_without_pref.replace(city1.group(1), "")
        remaining2 = addr2_without_pref.replace(city2.group(1), "")

        # 残りの部分の共通部分を計算
        common_chars = 0
        max_len = max(len(remaining1), len(remaining2))

        if max_len == 0:
            return 0.8  # 市区町村まで一致

        # 文字単位での一致度を計算
        for i in range(min(len(remaining1), len(remaining2))):
            if remaining1[i] == remaining2[i]:
                common_chars += 1
            else:
                break

        similarity = 0.6 + (common_chars / max_len) * 0.4
        return min(similarity, 1.0)

    # 都道府県のみ一致
    if pref1 and pref2 and pref1.group(1) == pref2.group(1):
        return 0.3

    return 0.0


# 動作確認用
# pipenv run python address_similarity.py
if __name__ == "__main__":
    similarity = calculate_address_similarity(
        "岩手県 FOO市 BAR佐倉河字BAZ71番地",
        "岩手県FOO市BAR区佐倉河字BAZ71",
    )
    print(f"{similarity:.2f}")

    similarity = calculate_address_similarity(
        "岩手県 FOO市 BAR佐倉河字BAZ71番地",
        "岩手県FOO市江刺区田原字横懸248-9",
    )
    print(f"{similarity:.2f}")

    similarity = calculate_address_similarity(
        "埼玉県BAR市中区BAZ三丁目8番16号",
        "〒541-0053 大阪府大阪市中央区本町４丁目４−１２",
    )
    print(f"{similarity:.2f}")

    similarity = calculate_address_similarity(
        "埼玉県BAR市中区BAZ三丁目8番16号",
        "埼玉県春日部市南栄町11-7",
    )
    print(f"{similarity:.2f}")

    similarity = calculate_address_similarity(
        "青森県FOO郡BAZ村大字BAR133番地70",
        "〒039-3213 青森県FOO郡BAZ村大字BAR１３３−７０",
    )
    print(f"{similarity:.2f}")

    similarity = calculate_address_similarity(
        "京都府FOO市BAR区大宮通仏光寺下る五坊大宮町9999番地",
        "名古屋市東区泉9丁目99番1号　9999ビル内",
    )
    print(f"{similarity:.2f}")
