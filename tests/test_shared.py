from shared import normalize_csv_data


def test_normalize_csv_data():
    assert normalize_csv_data("  A\r\nB\nC\rD   E  ") == "A B C D E"
    assert normalize_csv_data("") == ""
