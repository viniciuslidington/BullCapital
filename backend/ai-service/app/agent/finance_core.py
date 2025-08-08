# ia/valuation/finance_core.py
from __future__ import annotations
from functools import lru_cache
from datetime import datetime
from typing import Any, Dict, List, Optional

import yfinance as yf

__all__ = ["get_indicadores_avancados_com_valuation"]

def _safe_div(a, b):
    try:
        if a is None or b in (None, 0):
            return None
        return float(a) / float(b)
    except Exception:
        return None

def _mean(nums):
    nums = [float(x) for x in nums if x is not None]
    return sum(nums)/len(nums) if nums else None

@lru_cache(maxsize=64)
def _get_info_cached(tk: str) -> dict:
    t = yf.Ticker(tk)
    return t.info or {}

def _normalize_b3(ticker: str) -> str:
    if not ticker:
        return ticker
    if "." in ticker:
        return ticker
    # Se termina com dígito (ex.: PETR4) assume B3 e adiciona .SA
    return ticker + ".SA" if ticker[-1].isdigit() else ticker

def get_indicadores_avancados_com_valuation(
    ticker: str,
    peers: Optional[List[str]] = None,
    rf: float = 0.04,
    erp: float = 0.06,
    dr: float = 0.10,
    tax_rate: float = 0.25,
) -> Dict[str, Any]:
    """
    Núcleo: retorna dict com indicadores avançados + valuation.
    Robusto a campos ausentes (None) e com guard-rails simples.
    """
    tk = _normalize_b3(ticker)
    info = _get_info_cached(tk)
    warnings: List[str] = []

    # --- Básico ---
    shares = info.get("sharesOutstanding") or 1
    price  = info.get("regularMarketPrice")
    currency = info.get("currency") or "BRL"

    # Crescimento e CAPM
    g_raw = info.get("earningsQuarterlyGrowth", 0.05)
    try:
        g = float(g_raw) if g_raw is not None else 0.05
    except Exception:
        g = 0.05
    if dr <= g:
        g = max(0.0, dr - 0.01)
        warnings.append("g foi limitado para ficar abaixo da taxa de desconto (dr).")

    beta = info.get("beta")
    try:
        beta = float(beta) if beta is not None else 1.0
    except Exception:
        beta = 1.0
    ke = rf + beta * erp

    # --- Indicadores avançados ---
    ev      = info.get("enterpriseValue")
    ebitda  = info.get("ebitda")
    revenue = info.get("totalRevenue")

    ev_to_ebitda = _safe_div(ev, ebitda)
    ev_to_sales  = _safe_div(ev, revenue)

    total_debt   = info.get("totalDebt") or 0
    equity_mkt   = info.get("marketCap")
    if equity_mkt is None and price is not None:
        equity_mkt = float(price) * float(shares)

    total_equity_bs = info.get("totalStockholderEquity")
    debt_to_equity  = _safe_div(total_debt, total_equity_bs)

    indicadores = {
        "ticker": tk,
        "currency": currency,
        "price": price,
        "marketCap": equity_mkt,
        "enterpriseValue": ev,
        "trailingPE": info.get("trailingPE"),
        "forwardPE": info.get("forwardPE"),
        "pegRatio": info.get("pegRatio"),
        "priceToBook": info.get("priceToBook"),
        "priceToSales": info.get("priceToSalesTrailing12Months") or info.get("priceToSales"),
        "evToEbitda": ev_to_ebitda,
        "evToRevenue": ev_to_sales,
        "debtToEquity": debt_to_equity,
        "currentRatio": info.get("currentRatio"),
        "quickRatio": info.get("quickRatio"),
        "grossMargins": info.get("grossMargins"),
        "operatingMargins": info.get("operatingMargins"),
        "profitMargins": info.get("profitMargins"),
        "returnOnEquity": info.get("returnOnEquity"),
        "returnOnAssets": info.get("returnOnAssets"),
        "beta": beta,
        "dividendYield": info.get("dividendYield"),
        "payoutRatio": info.get("payoutRatio"),
        "freeCashFlow": info.get("freeCashflow"),
        "operatingCashflow": info.get("operatingCashflow"),
    }

    # --- Valuation ---
    # 1) DCF (5y + terminal)
    fcf = info.get("freeCashflow")
    dcf_price = None
    if fcf and dr > 0:
        try:
            fcf = float(fcf)
            proj = sum(fcf * (1 + g)**i / (1 + dr)**i for i in range(1, 6))
            term = (fcf * (1 + g)**5) * (1 + g) / (dr - g) if dr > g else None
            if term is None:
                warnings.append("Termo de perpetuidade não calculado (dr <= g).")
            else:
                dcf_price = (proj + term / (1 + dr)**5) / float(shares)
        except Exception:
            warnings.append("Falha ao calcular DCF.")

    # 2) Gordon (Dividendos)
    div = info.get("dividendRate") or info.get("forwardAnnualDividendRate") or 0
    try:
        div = float(div)
    except Exception:
        div = 0.0
    g_d = g * 0.6
    gordon = div * (1 + g_d) / (dr - g_d) if (div and dr > g_d) else None
    if div == 0:
        warnings.append("Sem dividendos: modelo de Gordon não aplicável.")

    # 3) EV/EBIT comparável
    if peers is None:
        peers = ["VALE3.SA", "ITUB4.SA", "BBDC4.SA"]
    peer_mults = []
    for p in peers:
        try:
            pi = _get_info_cached(p)
            ebit_peer = pi.get("ebit") or pi.get("ebitda")
            if pi.get("enterpriseValue") and ebit_peer:
                peer_mults.append(_safe_div(pi["enterpriseValue"], ebit_peer))
        except Exception:
            pass
    ev_mult = _mean(peer_mults)
    ebit_this = info.get("ebit") or info.get("ebitda")
    ev_based = None
    if ev_mult and ebit_this:
        try:
            ev_implied = ev_mult * float(ebit_this)
            ev_to_equity = ev_implied - float(total_debt or 0) + float(info.get("cash", 0) or 0)
            ev_based = ev_to_equity / float(shares)
        except Exception:
            warnings.append("Falha no EV/EBIT comparável.")

    # 4) P/L comparável
    peer_pl = []
    for p in peers:
        try:
            pl = _get_info_cached(p).get("trailingPE")
            if pl:
                peer_pl.append(float(pl))
        except Exception:
            pass
    pl_mult = _mean(peer_pl)
    eps = info.get("trailingEps")
    pl_price = float(pl_mult) * float(eps) if (pl_mult and eps) else None

    # 5) PEG: preço ~ PEG * EPS (heurística)
    peg = info.get("pegRatio")
    try:
        peg = float(peg) if peg is not None else None
    except Exception:
        peg = None
    peg_price = (peg * float(eps)) if (peg and eps) else None

    # 6) CAPM – preço via dividendos (opcional) & Ke
    capm_price = (div * (1 + g_d) / (ke - g_d)) if (div and ke > g_d) else None

    # WACC (simples)
    interest_exp = info.get("interestExpense")
    kd = _safe_div(abs(interest_exp) if interest_exp is not None else None, total_debt) or 0.08
    V = (equity_mkt or 0) + (total_debt or 0)
    wacc = ((equity_mkt or 0)/V) * ke + ((total_debt or 0)/V) * kd * (1 - tax_rate) if V else None

    precos = [x for x in [dcf_price, gordon, ev_based, pl_price, peg_price, capm_price] if x is not None]
    media_preco = _mean(precos)

    valuation = {
        "DCF_5y": round(dcf_price, 2) if dcf_price else None,
        "Gordon": round(gordon, 2) if gordon else None,
        "EV_EBIT_peerBased": round(ev_based, 2) if ev_based else None,
        "PL_peerBased": round(pl_price, 2) if pl_price else None,
        "PEG_based": round(peg_price, 2) if peg_price else None,
        "CAPM_price_via_div": round(capm_price, 2) if capm_price else None,
        "Media_precos": round(media_preco, 2) if media_preco else None,
        "Ke_CAPM_pct": round(ke * 100, 2) if ke else None,
        "WACC_pct": round(wacc * 100, 2) if wacc else None,
    }

    indicadores_clean = {k: v for k, v in indicadores.items() if v is not None}
    valuation_clean   = {k: v for k, v in valuation.items()   if v is not None}

    return {
        "meta": {
            "ticker": tk,
            "as_of": datetime.utcnow().isoformat() + "Z",
            "source": "yfinance",
            "currency": currency,
            "notes": warnings,
            "peers_used": peers,
            "assumptions": {"rf": rf, "erp": erp, "dr": dr, "tax_rate": tax_rate},
        },
        "indicadores": indicadores_clean,
        "valuation": valuation_clean,
    }