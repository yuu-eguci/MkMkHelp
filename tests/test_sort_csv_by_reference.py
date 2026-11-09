import pandas as pd

from sort_csv_by_reference import sort_by_reference_urls


def test_sort_by_reference_urls_follows_reference_order_and_appends_unmatched():
    reference = pd.DataFrame({"url": ["u2", "u9", "u1"]})
    target = pd.DataFrame({"name": ["a", "b", "c", "d"], "url": ["u1", "u2", "u3", "u2"]})

    result = sort_by_reference_urls(reference, target)

    assert list(result.columns) == ["name", "url"]
    assert result.to_dict("records") == [
        {"name": "b", "url": "u2"},
        {"name": "d", "url": "u2"},
        {"name": "a", "url": "u1"},
        {"name": "c", "url": "u3"},
    ]
