import pytest
from utils import fetch_ticker_data, get_exchange_rate, generate_pdf_report

def test_fetch_ticker_data():
    # Test a known ticker
    price, currency, err = fetch_ticker_data("AAPL")
    assert err is None
    assert price is not None
    assert price > 0
    assert currency == "USD"
    
    # Test an invalid ticker
    price, currency, err = fetch_ticker_data("INVALID_TICKER_123")
    assert err is not None
    assert price is None

def test_get_exchange_rate():
    # Same currency
    assert get_exchange_rate("USD", "USD") == 1.0
    
    # Valid pair
    rate = get_exchange_rate("EUR", "USD")
    assert rate is not None
    assert rate > 0

    # Invalid pair
    rate = get_exchange_rate("ZZZ", "YYY")
    assert rate is None

def test_generate_pdf_report():
    jars = [
        {"name": "Test Jar", "percent": 100, "amount": 1000},
        {"name": "FFA", "percent": 10, "amount": 100} # Index 1 for FFA
    ]
    pdf_bytes = generate_pdf_report(
        income=1000,
        currency="USD",
        jars=jars,
        ffa_ticker="AAPL",
        ffa_price=150.0,
        ffa_currency="USD",
        shares_to_buy=1,
        remaining_cash=850.0,
        lang="English"
    )
    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert len(pdf_bytes) > 0
