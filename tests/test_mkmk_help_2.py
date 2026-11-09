import sys

import pandas as pd

import mkmk_help_2
import shared

BASE_URL = "https://jn.example.invalid"

FOUND_HTML = """
<div class="frame-728-orange-l">
  <div class="title-background-orange"><a class="result" href="detail/0000000001">detail</a></div>
  <strong><a href="#">FOO株式会社</a></strong>
  <span class="red">0000000001 | 000-000-0001</span>
  <dl><dt>住所：東京都架空区1-1-1</dt></dl>
</div>
"""


def run_level2(monkeypatch, tmp_path, responses):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(mkmk_help_2, "sleep", lambda _: None)
    pd.DataFrame(
        {
            "name": ["FOO 株式会社", "BAR 株式会社", "BAZ 株式会社"],
            "location": ["東京都架空区1-1-1", "東京都架空区2-2-2", "東京都架空区3-3-3"],
            "url": [
                "https://jb.example.invalid/org/1",
                "https://jb.example.invalid/org/2",
                "https://jb.example.invalid/org/3",
            ],
        }
    ).to_csv("level1.csv", index=False)

    def fake_fetch(url, wait_sec=3):
        response = responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(shared, "fetch_html_slowly", fake_fetch)
    monkeypatch.setattr(
        sys,
        "argv",
        ["mkmk_help_2.py", "--csv", "level1.csv", "--jn-base-url", BASE_URL, "--output-csv", "level2.csv"],
    )
    mkmk_help_2.main()
    return pd.read_csv("level2.csv", dtype=str, keep_default_na=False).to_dict("records")


def test_level2_saves_rows_ending_with_401_or_error(monkeypatch, tmp_path):
    rows = run_level2(
        monkeypatch,
        tmp_path,
        [FOUND_HTML, "<h1>401 Error - Unauthorized Access</h1>", RuntimeError("synthetic failure")],
    )

    assert [row["name"] for row in rows] == ["FOO 株式会社", "BAR 株式会社", "BAZ 株式会社"]
    assert rows[0]["jn_tel"] == "0000000001"
    assert rows[0]["jn_detail_url"] == f"{BASE_URL}/detail/0000000001"
    assert rows[1]["jn_memo"] == "拒否されたわ401。ｱﾁｬｰ!"
    assert rows[2]["jn_memo"] == "なんかエラー起きたわ: synthetic failure"


def test_level2_writes_output_even_if_every_row_fails(monkeypatch, tmp_path):
    rows = run_level2(monkeypatch, tmp_path, [RuntimeError("a"), RuntimeError("b"), RuntimeError("c")])

    assert [row["jn_memo"] for row in rows] == [
        "なんかエラー起きたわ: a",
        "なんかエラー起きたわ: b",
        "なんかエラー起きたわ: c",
    ]
