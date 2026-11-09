import jn

SEARCH_HTML = """
<html><body>
<div class="frame-728-orange-l">
  <div class="title-background-orange"><a class="result" href="detail/0000000001">detail</a></div>
  <strong><a href="#">FOO株式会社</a></strong>
  <span class="red">0000000001 | 000-000-0001</span>
  <dl><dt>業種：架空</dt><dt>住所：東京都架空区1-2-3</dt></dl>
</div>
<div class="frame-728-orange-l">
  <strong><a href="#">電話番号なし</a></strong>
</div>
</body></html>
"""


def test_create_search_url():
    assert (
        jn.create_search_url("https://example.invalid", "FOO") == "https://example.invalid/searchnumber.do?number=FOO"
    )


def test_remove_spaces_removes_half_and_full_width_spaces():
    assert jn.remove_spaces(" F O　O ") == "FOO"


def test_parse_search_results_keeps_only_results_with_tel_and_name():
    assert jn.parse_search_results(SEARCH_HTML) == [
        {
            "tel": "0000000001 | 000-000-0001",
            "company_name": "FOO株式会社",
            "location": "東京都架空区1-2-3",
            "detail_url": "detail/0000000001",
        }
    ]


def test_find_best_match_by_location():
    results = [
        {"location": "東京都架空区9-9-9", "tel": "1"},
        {"location": "東京都架空区1-2-3", "tel": "2"},
    ]
    assert jn.find_best_match_by_location(results, "東京都架空区1丁目2番3号") == results[1]
    assert not jn.find_best_match_by_location(results, "大阪府架空市1-2-3")
    assert not jn.find_best_match_by_location([], "東京都架空区1-2-3")


def test_split_tel_field():
    assert jn.split_tel_field("0000000001 | 000-000-0001") == ("0000000001", "000-000-0001")
    assert jn.split_tel_field(" 0000000001 ") == ("0000000001", "")
