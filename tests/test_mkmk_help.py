import json
import sys

import pandas as pd
import requests

import mkmk_help

BASE_URL = "https://jb.example.invalid"

LIST_HTML = """
<table>
<tr class="ant-table-row ant-table-row-level-0"><td><a class="app-link" href="/org/1">FOO株式会社</a></td></tr>
<tr class="ant-table-row ant-table-row-level-0"><td><a class="app-link" href="/org/2">BAR株式会社</a></td></tr>
<tr class="ant-table-row ant-table-row-level-0"><td><a class="app-link" href="/org/3">BAZ株式会社</a></td></tr>
</table>
"""


def detail_html(location):
    data = {"props": {"pageProps": {"organization": {"attributes": {"location": location}}}}}
    return f'<script id="__NEXT_DATA__" type="application/json">{json.dumps(data, ensure_ascii=False)}</script>'


def test_level1_continues_when_detail_page_fails(monkeypatch, tmp_path):
    details = {
        f"{BASE_URL}/org/1": detail_html("東京都\n架空区1-1-1"),
        f"{BASE_URL}/org/2": "<html>no next data</html>",
        f"{BASE_URL}/org/3": requests.exceptions.ConnectionError("synthetic failure"),
    }

    def fake_fetch_html(url):
        detail = details[url]
        if isinstance(detail, Exception):
            raise detail
        return detail

    output_csv = tmp_path / "level1.csv"
    monkeypatch.setattr(mkmk_help, "fetch_html_slowly", lambda url, wait_sec=3: LIST_HTML)
    monkeypatch.setattr(mkmk_help, "fetch_html", fake_fetch_html)
    monkeypatch.setattr(mkmk_help, "sleep", lambda _: None)
    monkeypatch.setattr(
        sys,
        "argv",
        ["mkmk_help.py", "--base-url", BASE_URL, "--total-row", "3", "--output-csv", str(output_csv)],
    )

    mkmk_help.main()

    assert pd.read_csv(output_csv, dtype=str, keep_default_na=False).to_dict("records") == [
        {"name": "FOO株式会社", "location": "東京都 架空区1-1-1", "url": f"{BASE_URL}/org/1"},
        {"name": "BAR株式会社", "location": "", "url": f"{BASE_URL}/org/2"},
        {"name": "BAZ株式会社", "location": "", "url": f"{BASE_URL}/org/3"},
    ]
