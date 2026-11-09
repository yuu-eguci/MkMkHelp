import pytest

from address_similarity import calculate_address_similarity, normalize_address


def test_normalize_address_removes_postal_code_spaces_and_notation():
    assert normalize_address("〒100-0001 東京都 架空区 一丁目２番地３号") == "東京都架空区123"


def test_normalize_address_drops_ward_inside_city():
    assert normalize_address("岩手県FOO市BAR区佐倉河") == "岩手県FOO市BAR佐倉河"


@pytest.mark.parametrize(
    ("addr1", "addr2", "expected"),
    [
        ("岩手県 FOO市 BAR佐倉河字BAZ71番地", "岩手県FOO市BAR区佐倉河字BAZ71", 1.0),
        ("岩手県 FOO市 BAR佐倉河字BAZ71番地", "岩手県FOO市QUX区田原字横懸248-9", 0.6),
        ("埼玉県BAR市中区BAZ三丁目8番16号", "〒541-0053 大阪府QUX市中央区本町４丁目４−１２", 0.0),
        ("埼玉県BAR市中区BAZ三丁目8番16号", "埼玉県QUX市南栄町11-7", 0.3),
        ("青森県FOO郡BAZ村大字BAR133番地70", "〒039-3213 青森県FOO郡BAZ村大字BAR１３３−７０", 1.0),
        ("", "東京都架空区", 0.0),
    ],
)
def test_calculate_address_similarity(addr1, addr2, expected):
    assert calculate_address_similarity(addr1, addr2) == pytest.approx(expected)
