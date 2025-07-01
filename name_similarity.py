import re


def normalize_name_for_matching(name: str) -> str:
    """
    名前マッチング用の正規化
    法人格除去 + 記号除去 + スペース除去 + 小文字統一
    """
    if not name:
        return ""

    # 法人格除去
    normalized = remove_corporate_type(name)
    # 記号と全角英数字の正規化
    normalized = normalize_symbols_and_zenkaku(normalized)
    # スペース除去
    normalized = remove_spaces(normalized)
    # 小文字に統一
    normalized = normalized.lower()

    return normalized


def remove_spaces(name: str) -> str:
    """
    文字列をノーマライズする。
    スペース除去だけ
    """
    return name.replace(" ", "").replace("　", "")


def remove_corporate_type(name: str) -> str:
    """
    文字列をノーマライズする。
    法人格除去だけ (スペースは残す)
    """
    return re.sub(r"(株式|有限|合同)会社", "", name)


def normalize_symbols_and_zenkaku(name: str) -> str:
    """
    文字列をノーマライズする。
    全角英数字→半角 + 記号除去だけ (スペース除去なし)
    """
    name = name.translate(
        str.maketrans(
            "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ",
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        )
    )
    return re.sub(r"[‐\ーｰ・,、。!！?？（）()［］【】｛｝「」『』]", "", name)


def calculate_name_similarity(name1: str, name2: str, threshold: float = 0.7) -> float:
    """
    名前の類似度を計算 (0.0-1.0)
    Level 3 用: 住所で検索した結果から、名前でバリデーションする
    """
    if not name1 or not name2:
        return 0.0

    # 両方の名前を正規化
    name1_normalized = normalize_name_for_matching(name1)
    name2_normalized = normalize_name_for_matching(name2)

    # マッチング戦略:
    # 1. 完全一致
    if name1_normalized == name2_normalized:
        return 1.0

    # 2. 部分一致 (どちらかがもう一方に含まれる)
    elif name1_normalized in name2_normalized or name2_normalized in name1_normalized:
        # 短い方の長さに対する長い方の長さの比率で類似度を計算
        shorter_len = min(len(name1_normalized), len(name2_normalized))
        longer_len = max(len(name1_normalized), len(name2_normalized))
        return shorter_len / longer_len if longer_len > 0 else 0.0

    return 0.0


def find_best_match_by_name(search_results: list[dict], target_name: str, threshold: float = 0.7) -> dict | None:
    """
    検索結果から最適な名前マッチを見つける
    Level 3 用: 住所で検索した結果から、名前でバリデーションする
    """
    if not search_results:
        return None

    best_match = None
    best_score = 0.0

    for result in search_results:
        company_name = result.get("company_name", "")
        if not company_name:
            continue

        # 類似度を計算
        score = calculate_name_similarity(target_name, company_name)
        print(target_name, company_name, score)

        if score > best_score:
            best_score = score
            best_match = result

    # 閾値を超えた場合のみ返す
    if best_score >= threshold:
        return best_match

    return None


# 動作確認用
# pipenv run python name_similarity.py
if __name__ == "__main__":
    # テストケース
    test_cases = [
        ("FOO株式会社", "FOO"),
        ("BAR 株式会社", "BAR"),
        ("Baz Next Stage", "BazNextStage"),
        ("QUXロジテック 株式会社", "QUXロジテック"),
        ("全然違う会社", "別の会社"),
    ]

    for name1, name2 in test_cases:
        similarity = calculate_name_similarity(name1, name2)
        print(f"'{name1}' vs '{name2}': {similarity:.2f}")
