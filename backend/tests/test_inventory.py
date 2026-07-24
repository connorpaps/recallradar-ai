from app.services.text import parse_optional_date, parse_optional_decimal


def test_date_parser_accepts_iso_date() -> None:
    assert parse_optional_date("2026-07-22").isoformat() == "2026-07-22"


def test_date_parser_rejects_bad_date() -> None:
    assert parse_optional_date("07/22/2026") is None


def test_decimal_parser_rejects_bad_quantity() -> None:
    assert parse_optional_decimal("many") is None
