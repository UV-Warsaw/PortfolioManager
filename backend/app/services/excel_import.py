"""Excel import service — parses XTB export files into transaction and dividend records."""

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import UploadFile

from app.core.config import settings

logger = logging.getLogger("portfolio_backend.excel_import")

VALID_ACCOUNTS = ("IKE", "PLN", "USD")

# Header tokens used to auto-detect the header row in each sheet
_HEADER_TOKENS = {
    "position",
    "id",
    "type",
    "symbol",
    "time",
    "amount",
    "open time",
    "volume",
    "price",
}


def _find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first column name whose lower-case form contains any candidate string."""
    lc = {c.lower(): c for c in df.columns}
    for cand in candidates:
        for key, col in lc.items():
            if cand in key:
                return col
    return None


def _read_sheet_with_detected_header(xl: pd.ExcelFile, sheet_name: str) -> pd.DataFrame:
    """Parse a sheet, auto-detecting the header row by scanning for known column tokens."""
    raw = xl.parse(sheet_name=sheet_name, header=None)
    header_row: int | None = None
    for i, row in raw.iterrows():
        row_vals = {str(x).strip().lower() for x in row.tolist() if pd.notna(x)}
        if row_vals & _HEADER_TOKENS:
            header_row = i
            break
    if header_row is not None:
        try:
            return xl.parse(sheet_name=sheet_name, header=header_row)
        except Exception:
            pass
    return xl.parse(sheet_name=sheet_name)


def _safe_float(v: Any) -> float | None:
    try:
        if pd.isna(v):
            return None
        return float(v)
    except Exception:
        return None


def _safe_datetime(v: Any):
    try:
        if pd.isna(v):
            return None
        return pd.to_datetime(v).to_pydatetime()
    except Exception:
        return None


def _save_upload(upload: UploadFile) -> Path:
    """Persist the uploaded file to the data directory and return its path."""
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    dest = settings.data_dir / upload.filename
    upload.file.seek(0)
    dest.write_bytes(upload.file.read())
    return dest


def parse_excel_to_records(
    source: UploadFile | Path | str,
    account: str = "PLN",
) -> dict[str, list[dict]]:
    """
    Parse an XTB Excel export into lists of transaction and dividend dicts.

    Args:
        source: An uploaded file object or a filesystem path.
        account: Account type — one of IKE, PLN, USD.

    Returns:
        dict with keys ``transactions`` and ``dividends``, each a list of dicts.

    Raises:
        ValueError: If the file extension is not .xlsx or .xls.
    """
    acc = account.upper()

    if hasattr(source, "filename"):
        # UploadFile
        fname = (source.filename or "").lower()
        if not (fname.endswith(".xlsx") or fname.endswith(".xls")):
            raise ValueError("Only .xlsx and .xls files are supported")
        path = _save_upload(source)
    else:
        path = Path(source)
        if not (str(path).endswith(".xlsx") or str(path).endswith(".xls")):
            raise ValueError("Only .xlsx and .xls files are supported")

    rate = settings.usd_to_pln_rate
    xl = pd.ExcelFile(path)

    txs: list[dict] = []
    divs: list[dict] = []

    for sheet_name in xl.sheet_names:
        df = _read_sheet_with_detected_header(xl, sheet_name)
        if df is None or df.empty:
            continue

        lname = sheet_name.strip().lower()

        # ── OPEN POSITIONS ────────────────────────────────────────────────────
        if "open position" in lname:
            symbol_col = _find_col(df, ["symbol", "position"])
            volume_col = _find_col(df, ["volume"])
            open_time_col = _find_col(df, ["open time"])
            open_price_col = _find_col(df, ["open price"])
            market_price_col = _find_col(df, ["market price"])
            purchase_value_col = _find_col(df, ["purchase value"])

            for _, row in df.iterrows():
                ticker = (
                    str(row[symbol_col]).strip()
                    if symbol_col and pd.notna(row[symbol_col])
                    else None
                )
                qty = _safe_float(row[volume_col]) if volume_col else None
                date = _safe_datetime(row[open_time_col]) if open_time_col else None
                price = _safe_float(row[open_price_col]) if open_price_col else None
                market_price = (
                    _safe_float(row[market_price_col]) if market_price_col else None
                )
                amount = (
                    _safe_float(row[purchase_value_col]) if purchase_value_col else None
                )

                if acc == "USD":
                    if price is not None:
                        price = price * rate
                    if market_price is not None:
                        market_price = market_price * rate
                    if amount is not None:
                        amount = amount * rate

                if ticker and qty and qty > 0:
                    txs.append(
                        {
                            "date": date,
                            "ticker": ticker,
                            "type": "BUY",
                            "quantity": qty,
                            "price": price,
                            "market_price": market_price,
                            "amount": amount,
                            "raw": json.dumps(row.dropna().to_dict(), default=str),
                            "account": acc,
                        }
                    )
            continue

        # ── CLOSED POSITIONS — skip ───────────────────────────────────────────
        if "closed" in lname:
            continue

        # ── CASH OPERATIONS ───────────────────────────────────────────────────
        if "cash" in lname:
            type_col = _find_col(df, ["type", "operation"])
            symbol_col = _find_col(df, ["symbol", "instrument", "comment"])
            time_col = _find_col(df, ["time", "date"])
            amount_col = _find_col(df, ["amount", "value", "cash"])

            by_key: dict[tuple, dict] = {}
            for _, row in df.iterrows():
                try:
                    typ = (
                        str(row[type_col]).strip()
                        if type_col and pd.notna(row[type_col])
                        else ""
                    )
                except Exception:
                    typ = ""
                try:
                    sym = (
                        str(row[symbol_col]).strip()
                        if symbol_col and pd.notna(row[symbol_col])
                        else None
                    )
                except Exception:
                    sym = None

                amt = _safe_float(row[amount_col]) or 0.0
                dt = _safe_datetime(row[time_col])

                if acc == "USD":
                    amt = amt * rate

                ltyp = typ.lower()
                key = (sym, dt.date() if dt is not None else None)
                if key not in by_key:
                    by_key[key] = {
                        "dividend": 0.0,
                        "tax": 0.0,
                        "date": dt,
                        "symbol": sym,
                    }
                if "div" in ltyp:
                    by_key[key]["dividend"] += amt
                elif "withhold" in ltyp or "tax" in ltyp:
                    by_key[key]["tax"] += amt

                if typ:
                    txs.append(
                        {
                            "date": dt,
                            "ticker": None,
                            "type": typ,
                            "quantity": None,
                            "price": None,
                            "amount": amt,
                            "raw": json.dumps(
                                {"type": typ, "symbol": sym, "amount": amt},
                                default=str,
                            ),
                            "account": acc,
                        }
                    )

            for parts in by_key.values():
                net = float(parts["dividend"] + parts["tax"])
                if parts["symbol"] is None and net == 0.0:
                    continue
                divs.append(
                    {
                        "date": parts["date"],
                        "ticker": parts["symbol"],
                        "amount": net,
                        "currency": None,
                        "raw": json.dumps(parts, default=str),
                        "account": acc,
                    }
                )

    logger.info(
        "Parsed %d transactions and %d dividends from %s (account=%s)",
        len(txs),
        len(divs),
        path.name,
        acc,
    )
    return {"transactions": txs, "dividends": divs}
