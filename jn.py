import re

from bs4 import BeautifulSoup

from address_similarity import calculate_address_similarity


def create_search_url(base_url: str, search_term: str) -> str:
    """検索 URL を作成する"""
    return f"{base_url}/searchnumber.do?number={search_term}"


# 文字列をノーマライズする。
# スペース除去だけ
def remove_spaces(name: str) -> str:
    return name.replace(" ", "").replace("　", "")


# 文字列をノーマライズする。
# 法人格除去だけ (スペースは残す)
def remove_corporate_type(name: str) -> str:
    return re.sub(r"(株式|有限|合同)会社", "", name)


# 文字列をノーマライズする。
# 全角英数字→半角 + 記号除去だけ (スペース除去なし)
def normalize_symbols_and_zenkaku(name: str) -> str:
    name = name.translate(
        str.maketrans(
            "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ",
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        )
    )
    return re.sub(r"[‐\ーｰ・,、。!！?？（）()［］【】｛｝「」『』]", "", name)


def parse_search_results(html: str) -> list[dict]:
    """
    検索結果を解析して必要なデータを抽出
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []

    # 検索結果のメインコンテナを取得
    search_result_divs = soup.select("div.frame-728-orange-l")

    for div in search_result_divs:
        try:
            # 電話番号を取得 (span.red から)
            tel_span = div.select_one("span.red")
            tel = tel_span.get_text(strip=True) if tel_span else ""

            # 事業者名を取得 (strong > a から)
            company_link = div.select_one("strong > a")
            company_name = company_link.get_text(strip=True) if company_link else ""

            # 詳細URLを取得 (タイトル部分の a.result から)
            title_link = div.select_one("div.title-background-orange a.result")
            detail_url = title_link.get("href") if title_link else ""

            # 住所を取得 (「住所：」で始まる dt から)
            location = ""
            dt_elements = div.select("dt")
            for dt in dt_elements:
                text = dt.get_text(strip=True)
                if text.startswith("住所："):
                    location = text.replace("住所：", "").strip()
                    break

            # データが揃っている場合のみ結果に追加
            if tel and company_name:
                results.append(
                    {"tel": tel, "company_name": company_name, "location": location, "detail_url": detail_url}
                )

        except Exception:
            # 個別の解析エラーは無視して次の結果へ
            continue

    return results


def find_best_match_by_location(
    search_results: list[dict], target_location: str, threshold: float = 0.7
) -> dict | None:
    """
    検索結果から最適な住所マッチを見つける
    """
    if not search_results:
        return {}

    best_match = None
    best_score = 0.0

    for result in search_results:
        score = calculate_address_similarity(target_location, result.get("location", ""))

        if score > best_score:
            best_score = score
            best_match = result

    # 閾値を超えた場合のみ返す
    if best_score >= threshold:
        return best_match

    return None


def split_tel_field(tel_field: str) -> tuple[str, str]:
    """
    電話番号フィールドを分割する。
    例: '7777889999 | 7777-88-9999' → ('7777889999', '7777-88-9999')
         '0123456789' → ('0123456789', '')
    """
    if "|" in tel_field:
        parts = [p.strip() for p in tel_field.split("|")]
        return (parts[0], parts[1] if len(parts) > 1 else "")
    return (tel_field.strip(), "")
