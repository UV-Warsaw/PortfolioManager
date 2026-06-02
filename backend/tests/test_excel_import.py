"""Tests for the Excel import service and /portfolio/upload endpoint."""

import io
from pathlib import Path

import pandas as pd
import pytest

from app.services.excel_import import parse_excel_to_records

# ── helpers ──────────────────────────────────────────────────────────────────


def _make_excel(
    tmp_path: Path, open_positions: bool = True, cash_ops: bool = True
) -> Path:
    """Build a minimal synthetic XTB-style Excel file."""
    xlsx = tmp_path / "portfolio.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        if open_positions:
            pd.DataFrame(
                {
                    "Symbol": ["AAPL", "GOOGL"],
                    "Volume": [10.0, 5.0],
                    "Open Time": ["2023-01-15 10:30:00", "2023-02-01 14:20:00"],
                    "Open Price": [150.0, 2500.0],
                    "Market Price": [155.0, 2600.0],
                    "Purchase Value": [1500.0, 12500.0],
                }
            ).to_excel(writer, sheet_name="Open Position", index=False)
        if cash_ops:
            pd.DataFrame(
                {
                    "Type": ["Dividend", "Withholding Tax"],
                    "Symbol": ["AAPL", "AAPL"],
                    "Time": ["2023-03-15 00:00:00", "2023-03-15 00:00:00"],
                    "Amount": [30.0, -5.0],
                }
            ).to_excel(writer, sheet_name="Cash Operation", index=False)
    return xlsx


# ── unit tests — service ──────────────────────────────────────────────────────


def test_parse_excel_returns_transactions(tmp_path: Path) -> None:
    xlsx = _make_excel(tmp_path)
    result = parse_excel_to_records(xlsx, account="PLN")
    assert len(result["transactions"]) >= 2


def test_parse_excel_returns_dividends(tmp_path: Path) -> None:
    xlsx = _make_excel(tmp_path)
    result = parse_excel_to_records(xlsx, account="PLN")
    assert len(result["dividends"]) >= 1


def test_parse_excel_transaction_fields(tmp_path: Path) -> None:
    xlsx = _make_excel(tmp_path)
    result = parse_excel_to_records(xlsx, account="PLN")
    tx = next(t for t in result["transactions"] if t.get("ticker") == "AAPL")
    assert tx["type"] == "BUY"
    assert tx["quantity"] == 10.0
    assert tx["account"] == "PLN"


def test_parse_excel_usd_rate_applied(tmp_path: Path) -> None:
    xlsx = _make_excel(tmp_path, cash_ops=False)
    result_pln = parse_excel_to_records(xlsx, account="PLN")
    result_usd = parse_excel_to_records(xlsx, account="USD")

    tx_pln = next(t for t in result_pln["transactions"] if t.get("ticker") == "AAPL")
    tx_usd = next(t for t in result_usd["transactions"] if t.get("ticker") == "AAPL")

    assert tx_usd["price"] > tx_pln["price"]  # USD prices are multiplied by rate


def test_parse_excel_closed_positions_skipped(tmp_path: Path) -> None:
    xlsx = tmp_path / "closed.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        pd.DataFrame({"Symbol": ["X"], "Volume": [1]}).to_excel(
            writer, sheet_name="Closed Position History", index=False
        )
    result = parse_excel_to_records(xlsx, account="PLN")
    assert result["transactions"] == []


def test_parse_excel_unknown_columns_ignored(tmp_path: Path) -> None:
    xlsx = tmp_path / "extra_cols.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        pd.DataFrame(
            {
                "Symbol": ["MSFT"],
                "Volume": [3.0],
                "Open Time": ["2023-05-01 09:00:00"],
                "Open Price": [300.0],
                "Purchase Value": [900.0],
                "UnknownColumnXYZ": ["ignore me"],
            }
        ).to_excel(writer, sheet_name="Open Position", index=False)
    result = parse_excel_to_records(xlsx, account="PLN")
    assert len(result["transactions"]) == 1
    assert result["transactions"][0]["ticker"] == "MSFT"


def test_parse_excel_invalid_extension_raises(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("Symbol,Volume\nAAPL,10\n")
    with pytest.raises(ValueError, match="xlsx"):
        parse_excel_to_records(csv_file, account="PLN")


def test_parse_excel_empty_sheet_ok(tmp_path: Path) -> None:
    xlsx = tmp_path / "empty.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        pd.DataFrame().to_excel(writer, sheet_name="Open Position", index=False)
    result = parse_excel_to_records(xlsx, account="PLN")
    assert result["transactions"] == []
    assert result["dividends"] == []


# ── integration tests — router ────────────────────────────────────────────────


def _register_and_login(client) -> str:
    """Register a user and return a valid JWT token."""
    client.post(
        "/auth/register",
        json={"email": "import@test.com", "password": "Password1!"},
    )
    res = client.post(
        "/auth/login",
        json={"email": "import@test.com", "password": "Password1!"},
    )
    return res.json()["access_token"]


def test_upload_endpoint_success(client, tmp_path: Path) -> None:
    token = _register_and_login(client)
    xlsx = _make_excel(tmp_path)

    with xlsx.open("rb") as f:
        res = client.post(
            "/portfolio/upload",
            data={"account": "PLN"},
            files={
                "file": (
                    "portfolio.xlsx",
                    f,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    assert res.status_code == 200
    body = res.json()
    assert body["account"] == "PLN"
    assert body["imported_transactions"] >= 2
    assert body["imported_dividends"] >= 1


def test_upload_endpoint_invalid_account(client, tmp_path: Path) -> None:
    token = _register_and_login(client)
    xlsx = _make_excel(tmp_path)

    with xlsx.open("rb") as f:
        res = client.post(
            "/portfolio/upload",
            data={"account": "INVALID"},
            files={
                "file": (
                    "portfolio.xlsx",
                    f,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    assert res.status_code == 400
    assert "account" in res.json()["detail"].lower()


def test_upload_endpoint_wrong_format(client) -> None:
    token = _register_and_login(client)
    csv_bytes = b"Symbol,Volume\nAAPL,10\n"

    res = client.post(
        "/portfolio/upload",
        data={"account": "PLN"},
        files={"file": ("data.csv", io.BytesIO(csv_bytes), "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 400
    assert "xlsx" in res.json()["detail"].lower()


def test_upload_endpoint_unauthenticated(client, tmp_path: Path) -> None:
    xlsx = _make_excel(tmp_path)

    with xlsx.open("rb") as f:
        res = client.post(
            "/portfolio/upload",
            data={"account": "PLN"},
            files={
                "file": (
                    "portfolio.xlsx",
                    f,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )

    assert res.status_code in (401, 403)
