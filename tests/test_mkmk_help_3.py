import sys

import pandas as pd

import mkmk_help_3
import shared

BASE_URL = "https://jn.example.invalid"

SEARCH_HTML = """
<div class="frame-728-orange-l">
  <div class="title-background-orange"><a class="result" href="detail/0000000002">detail</a></div>
  <strong><a href="#">BAR</a></strong>
  <span class="red">0000000002 | 000-000-0002</span>
  <dl><dt>住所：東京都架空区2-2-2</dt></dl>
</div>
"""

COLUMNS = [
    "name",
    "location",
    "url",
    "name_no_space",
    "jn_search_url",
    "jn_tel",
    "jn_tel_hyphen",
    "jn_company_name",
    "jn_location",
    "jn_detail_url",
    "jn_memo",
]


def write_level2_csv(path):
    rows = [
        {
            "name": "FOO株式会社",
            "location": "東京都架空区1-1-1",
            "url": "https://jb.example.invalid/org/1",
            "name_no_space": "FOO株式会社",
            "jn_search_url": f"{BASE_URL}/searchnumber.do?number=FOO株式会社",
            "jn_tel": "0000000001",
            "jn_tel_hyphen": "000-000-0001",
            "jn_company_name": "FOO",
            "jn_location": "東京都架空区1-1-1",
            "jn_detail_url": f"{BASE_URL}/detail/0000000001",
            "jn_memo": "",
        },
        {
            "name": "BAR株式会社",
            "location": "東京都 架空区 2-2-2",
            "url": "https://jb.example.invalid/org/2",
            "name_no_space": "BAR株式会社",
            "jn_search_url": f"{BASE_URL}/searchnumber.do?number=BAR株式会社",
            "jn_tel": "",
            "jn_tel_hyphen": "",
            "jn_company_name": "",
            "jn_location": "",
            "jn_detail_url": "",
            "jn_memo": "なんかこれは見つからなかったわ。",
        },
    ]
    pd.DataFrame(rows, columns=COLUMNS).to_csv(path, index=False, encoding="utf_8_sig")


def run_level3(monkeypatch, tmp_path):
    input_csv = tmp_path / "level2.csv"
    output_csv = tmp_path / "level3.csv"
    write_level2_csv(input_csv)

    fetched_urls = []

    def fake_fetch(url, wait_sec=3):
        fetched_urls.append(url)
        return SEARCH_HTML

    monkeypatch.setattr(shared, "fetch_html_slowly", fake_fetch)
    monkeypatch.setattr(
        sys,
        "argv",
        ["mkmk_help_3.py", "--csv", str(input_csv), "--jn-base-url", BASE_URL, "--output-csv", str(output_csv)],
    )
    mkmk_help_3.main()

    output = pd.read_csv(output_csv, dtype=str, keep_default_na=False)
    return fetched_urls, output.to_dict("records")


def test_level3_keeps_rows_already_filled_by_level2(monkeypatch, tmp_path):
    fetched_urls, rows = run_level3(monkeypatch, tmp_path)

    assert fetched_urls == [f"{BASE_URL}/searchnumber.do?number=東京都架空区2-2-2"]
    assert rows[0]["jn_tel"] == "0000000001"
    assert rows[0]["jn_tel_hyphen"] == "000-000-0001"
    assert rows[0]["jn_company_name"] == "FOO"
    assert rows[0]["jn_location"] == "東京都架空区1-1-1"
    assert rows[0]["jn_detail_url"] == f"{BASE_URL}/detail/0000000001"
    assert rows[0]["jn_search_url"] == f"{BASE_URL}/searchnumber.do?number=FOO株式会社"


def test_level3_fills_empty_rows_by_location_search(monkeypatch, tmp_path):
    _, rows = run_level3(monkeypatch, tmp_path)

    assert rows[1]["location_no_space"] == "東京都架空区2-2-2"
    assert rows[1]["jn_search_url"] == f"{BASE_URL}/searchnumber.do?number=東京都架空区2-2-2"
    assert rows[1]["jn_tel"] == "0000000002"
    assert rows[1]["jn_tel_hyphen"] == "000-000-0002"
    assert rows[1]["jn_company_name"] == "BAR"
    assert rows[1]["jn_detail_url"] == f"{BASE_URL}/detail/0000000002"
    assert rows[1]["jn_memo"] == "住所検索で電話番号を埋めた。"


def test_level3_can_rerun_on_its_own_output(monkeypatch, tmp_path):
    run_level3(monkeypatch, tmp_path)
    level3_csv = tmp_path / "level3.csv"
    rerun_csv = tmp_path / "rerun.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        ["mkmk_help_3.py", "--csv", str(level3_csv), "--jn-base-url", BASE_URL, "--output-csv", str(rerun_csv)],
    )

    mkmk_help_3.main()

    assert pd.read_csv(rerun_csv, dtype=str, keep_default_na=False).equals(
        pd.read_csv(level3_csv, dtype=str, keep_default_na=False)
    )
