import json

import pytest

import jb

LIST_HTML = """
<table>
<tr class="ant-table-row ant-table-row-level-0"><td><a class="app-link" href="/org/1">FOO株式会社</a></td></tr>
<tr class="ant-table-row ant-table-row-level-0"><td><a class="app-link" href="">リンクなし</a></td></tr>
<tr class="other-row"><td><a class="app-link" href="/org/2">対象外</a></td></tr>
</table>
"""


def test_extract_organizations_from_html():
    assert jb.extract_organizations_from_html(LIST_HTML) == [{"name": "FOO株式会社", "path": "/org/1"}]


def test_extract_next_data_from_html():
    data = {"props": {"pageProps": {"organization": {"attributes": {"location": "東京都架空区"}}}}}
    html = f'<script id="__NEXT_DATA__" type="application/json">{json.dumps(data)}</script>'
    assert jb.extract_next_data_from_html(html) == data
    assert jb.extract_next_data_from_html("<html></html>") == {}


def test_extract_next_data_from_html_raises_on_broken_json():
    with pytest.raises(json.JSONDecodeError):
        jb.extract_next_data_from_html('<script id="__NEXT_DATA__">{broken</script>')


def test_build_organization_data_normalizes_newlines():
    assert jb.build_organization_data("FOO\r\n株式会社", "東京都\n架空区  1-2-3", "https://example.invalid/org/1") == {
        "name": "FOO 株式会社",
        "location": "東京都 架空区 1-2-3",
        "url": "https://example.invalid/org/1",
    }
