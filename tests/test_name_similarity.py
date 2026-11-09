import pytest

from name_similarity import calculate_name_similarity, find_best_match_by_name, normalize_name_for_matching


def test_normalize_name_for_matching():
    assert normalize_name_for_matching("ＦＯＯ・バー 株式会社") == "fooバ"


@pytest.mark.parametrize(
    ("name1", "name2", "expected"),
    [
        ("FOO株式会社", "FOO", 1.0),
        ("BAR 株式会社", "BAR", 1.0),
        ("Baz Next Stage", "BazNextStage", 1.0),
        ("QUXロジテック 株式会社", "QUXロジテック", 1.0),
        ("FOOBAR", "FOO", 0.5),
        ("全然違う会社", "別の会社", 0.0),
        ("", "FOO", 0.0),
    ],
)
def test_calculate_name_similarity(name1, name2, expected):
    assert calculate_name_similarity(name1, name2) == pytest.approx(expected)


def test_find_best_match_by_name_picks_highest_score_above_threshold():
    results = [
        {"company_name": "FOOBAR", "tel": "1"},
        {"company_name": "FOO", "tel": "2"},
        {"company_name": "", "tel": "3"},
    ]
    assert find_best_match_by_name(results, "FOO株式会社") == {"company_name": "FOO", "tel": "2"}


def test_find_best_match_by_name_returns_none_below_threshold_or_empty():
    assert find_best_match_by_name([{"company_name": "FOOBAR"}], "FOO") is None
    assert find_best_match_by_name([], "FOO") is None
