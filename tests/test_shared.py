import pytest

import shared
from shared import normalize_csv_data


def test_normalize_csv_data():
    assert normalize_csv_data("  A\r\nB\nC\rD   E  ") == "A B C D E"
    assert normalize_csv_data("") == ""


class FakeDriver:
    def __init__(self, error=None):
        self.error = error
        self.page_source = "<html>synthetic</html>"
        self.quit_called = False

    def execute_script(self, script):
        pass

    def get(self, url):
        if self.error:
            raise self.error

    def quit(self):
        self.quit_called = True


def test_fetch_html_slowly_returns_page_source_and_quits(monkeypatch):
    driver = FakeDriver()
    monkeypatch.setattr(shared.webdriver, "Chrome", lambda options: driver)
    monkeypatch.setattr(shared.time, "sleep", lambda _: None)

    assert shared.fetch_html_slowly("https://example.invalid", wait_sec=0) == "<html>synthetic</html>"
    assert driver.quit_called


def test_fetch_html_slowly_quits_driver_when_page_load_fails(monkeypatch):
    driver = FakeDriver(error=RuntimeError("synthetic failure"))
    monkeypatch.setattr(shared.webdriver, "Chrome", lambda options: driver)
    monkeypatch.setattr(shared.time, "sleep", lambda _: None)

    with pytest.raises(RuntimeError):
        shared.fetch_html_slowly("https://example.invalid", wait_sec=0)
    assert driver.quit_called
