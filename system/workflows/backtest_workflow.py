from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from system.workflows._helpers import (
    leader_packet,
    metadata,
    new_workflow_id,
    root_path,
    write_json,
    write_leader_packet,
    write_text,
)


SUPPORTED_STRATEGIES = {
    "example_ma_cross_v1",
    "classic_time_series_momentum_v1",
    "classic_cross_sectional_momentum_v1",
    "classic_mean_reversion_v1",
    "classic_pairs_trading_v1",
    "advanced_regime_aware_trend_v1",
    "advanced_dual_momentum_rotation_v1",
    "advanced_volatility_target_momentum_v1",
    "advanced_breakout_channel_v1",
    "advanced_rsi2_mean_reversion_v1",
    "advanced_kalman_pairs_trading_v1",
    "advanced_residual_stat_arb_v1",
}

PRICE_DIRS = (
    Path("data/normalized/prices"),
    Path("data/raw/massive"),
    Path("data/raw/quantconnect"),
)


def run(strategy_id: str = "example_ma_cross_v1", root: str | Path | None = None, workflow_id: str | None = None) -> dict:
    root_dir = root_path(root)
    workflow_id = workflow_id or new_workflow_id("backtest")
    run_dir = root_dir / "workspace" / "active_runs" / workflow_id
    run_dir.mkdir(parents=True, exist_ok=True)

    leader = leader_packet(workflow_id, f"backtest workflow for {strategy_id}", "backtest_workflow")
    leader_packet_path = write_leader_packet(root_dir, run_dir, leader)

    experiment_id = f"exp_{workflow_id}_{strategy_id}"
    candidate_dir = root_dir / "workspace" / "promotion_queue" / "candidate_experiments" / experiment_id
    candidate_dir.mkdir(parents=True, exist_ok=True)

    params = _load_strategy_params(root_dir, strategy_id)
    price_data = _load_price_data(root_dir)
    cost_model = {"commission": "not_configured", "amount": 0}
    slippage_model = {"model": "not_configured", "bps": 0}
    code_version = "local-quick-backtest-v1"

    results = _run_local_backtest(strategy_id, price_data, params)
    status = results["status"]
    data_version = {
        "vendor": "local_csv",
        "price_dirs": [str(path) for path in PRICE_DIRS],
        "symbols": sorted(price_data),
        "workflow_id": workflow_id,
    }

    write_text(candidate_dir / "experiment.yaml", f"experiment_id: {experiment_id}\nstrategy_id: {strategy_id}\nstatus: {status}\n")
    write_json(candidate_dir / "data_version.json", data_version)
    write_text(candidate_dir / "code_version.txt", code_version + "\n")
    write_json(candidate_dir / "params.json", params)
    write_json(candidate_dir / "cost_model.json", cost_model)
    write_json(candidate_dir / "slippage_model.json", slippage_model)
    write_json(candidate_dir / "results.json", results)
    write_text(candidate_dir / "review.md", _review_text(strategy_id, results))
    write_json(candidate_dir / "metadata.json", metadata(workflow_id, "backtest_workflow", "QuantEngineeringAgent"))

    return {
        "workflow_id": workflow_id,
        "experiment_id": experiment_id,
        "candidate_dir": str(candidate_dir),
        "leader_packet": str(leader_packet_path),
        "status": status,
    }


def run_many(strategy_ids: list[str], root: str | Path | None = None, workflow_id: str | None = None) -> dict:
    workflow_id = workflow_id or new_workflow_id("backtest")
    results = [run(strategy_id=strategy_id, root=root, workflow_id=f"{workflow_id}_{i + 1}") for i, strategy_id in enumerate(strategy_ids)]
    return {
        "workflow_id": workflow_id,
        "strategy_count": len(strategy_ids),
        "results": results,
    }


def _run_local_backtest(
    strategy_id: str,
    price_data: dict[str, list[tuple[str, float]]],
    params: dict[str, Any],
) -> dict[str, Any]:
    if strategy_id not in SUPPORTED_STRATEGIES:
        return {
            "status": "unsupported_strategy_for_local_engine",
            "reason": f"{strategy_id} requires data or logic not supported by the local quick backtest engine",
            "metrics": {},
        }
    if not price_data:
        return {
            "status": "blocked_no_price_data",
            "reason": "No local CSV price data found under data/normalized/prices, data/raw/massive, or data/raw/quantconnect",
            "metrics": {},
        }

    if strategy_id == "classic_cross_sectional_momentum_v1":
        return _backtest_cross_sectional_momentum(price_data, params)
    if strategy_id == "advanced_dual_momentum_rotation_v1":
        return _backtest_dual_momentum_rotation(price_data, params)
    if strategy_id == "classic_pairs_trading_v1":
        return _backtest_pairs_trading(price_data, params)
    if strategy_id == "advanced_kalman_pairs_trading_v1":
        return _backtest_dynamic_pairs_trading(strategy_id, price_data, params)
    if strategy_id == "advanced_residual_stat_arb_v1":
        return _backtest_residual_stat_arb(price_data, params)

    symbol = sorted(price_data)[0]
    series = price_data[symbol]
    if strategy_id == "classic_time_series_momentum_v1":
        daily_returns = _time_series_momentum_returns(series, params)
    elif strategy_id == "classic_mean_reversion_v1":
        daily_returns = _mean_reversion_returns(series, params)
    elif strategy_id == "advanced_regime_aware_trend_v1":
        daily_returns = _regime_aware_trend_returns(series, params)
    elif strategy_id == "advanced_volatility_target_momentum_v1":
        daily_returns = _volatility_target_momentum_returns(series, params)
    elif strategy_id == "advanced_breakout_channel_v1":
        daily_returns = _breakout_channel_returns(series, params)
    elif strategy_id == "advanced_rsi2_mean_reversion_v1":
        daily_returns = _rsi2_mean_reversion_returns(series, params)
    else:
        daily_returns = _moving_average_cross_returns(series, params)

    return _result_from_returns(strategy_id, [symbol], daily_returns)


def _moving_average_cross_returns(series: list[tuple[str, float]], params: dict[str, Any]) -> list[float]:
    fast_window = int(params.get("fast_window", 20))
    slow_window = int(params.get("slow_window", 50))
    closes = [price for _, price in series]
    daily_returns: list[float] = []
    position = 0.0

    for idx in range(1, len(closes)):
        if idx >= slow_window:
            fast_ma = mean(closes[idx - fast_window:idx])
            slow_ma = mean(closes[idx - slow_window:idx])
            position = 1.0 if fast_ma > slow_ma else 0.0
        daily_returns.append(position * _simple_return(closes[idx - 1], closes[idx]))
    return daily_returns


def _time_series_momentum_returns(series: list[tuple[str, float]], params: dict[str, Any]) -> list[float]:
    lookback_days = int(params.get("lookback_days", 252))
    deadband = float(params.get("deadband", 0.0))
    max_single_position = float(params.get("max_single_position", 0.05))
    closes = [price for _, price in series]
    daily_returns: list[float] = []

    for idx in range(1, len(closes)):
        position = 0.0
        if idx > lookback_days:
            lookback_return = _simple_return(closes[idx - lookback_days - 1], closes[idx - 1])
            position = max_single_position if lookback_return > deadband else 0.0
        daily_returns.append(position * _simple_return(closes[idx - 1], closes[idx]))
    return daily_returns


def _regime_aware_trend_returns(series: list[tuple[str, float]], params: dict[str, Any]) -> list[float]:
    lookback_days = int(params.get("lookback_days", 126))
    volatility_window = int(params.get("volatility_window", 20))
    max_volatility = float(params.get("max_volatility", 0.35))
    max_single_position = float(params.get("max_single_position", 0.05))
    deadband = float(params.get("deadband", 0.0))
    closes = [price for _, price in series]
    raw_returns = [_simple_return(closes[idx - 1], closes[idx]) for idx in range(1, len(closes))]
    daily_returns: list[float] = []

    for idx, asset_return in enumerate(raw_returns, start=1):
        position = 0.0
        if idx > max(lookback_days, volatility_window):
            lookback_return = _simple_return(closes[idx - lookback_days - 1], closes[idx - 1])
            realized_volatility = _annualized_volatility(raw_returns[idx - volatility_window:idx])
            if lookback_return > deadband and realized_volatility <= max_volatility:
                position = max_single_position
        daily_returns.append(position * asset_return)
    return daily_returns


def _volatility_target_momentum_returns(series: list[tuple[str, float]], params: dict[str, Any]) -> list[float]:
    lookback_days = int(params.get("lookback_days", 126))
    volatility_window = int(params.get("volatility_window", 20))
    target_volatility = float(params.get("target_volatility", 0.10))
    max_single_position = float(params.get("max_single_position", 0.10))
    deadband = float(params.get("deadband", 0.0))
    closes = [price for _, price in series]
    raw_returns = [_simple_return(closes[idx - 1], closes[idx]) for idx in range(1, len(closes))]
    daily_returns: list[float] = []

    for idx, asset_return in enumerate(raw_returns, start=1):
        position = 0.0
        if idx > max(lookback_days, volatility_window):
            lookback_return = _simple_return(closes[idx - lookback_days - 1], closes[idx - 1])
            realized_volatility = _annualized_volatility(raw_returns[idx - volatility_window:idx])
            if lookback_return > deadband and realized_volatility > 0:
                position = min(max_single_position, max_single_position * target_volatility / realized_volatility)
        daily_returns.append(position * asset_return)
    return daily_returns


def _breakout_channel_returns(series: list[tuple[str, float]], params: dict[str, Any]) -> list[float]:
    entry_window = int(params.get("entry_window", 55))
    exit_window = int(params.get("exit_window", 20))
    max_single_position = float(params.get("max_single_position", 0.05))
    closes = [price for _, price in series]
    daily_returns: list[float] = []
    position = 0.0

    for idx in range(1, len(closes)):
        if idx > max(entry_window, exit_window):
            entry_high = max(closes[idx - entry_window - 1:idx - 1])
            exit_low = min(closes[idx - exit_window - 1:idx - 1])
            if closes[idx - 1] > entry_high:
                position = max_single_position
            elif closes[idx - 1] < exit_low:
                position = 0.0
        daily_returns.append(position * _simple_return(closes[idx - 1], closes[idx]))
    return daily_returns


def _rsi2_mean_reversion_returns(series: list[tuple[str, float]], params: dict[str, Any]) -> list[float]:
    rsi_window = int(params.get("rsi_window", 2))
    entry_rsi = float(params.get("entry_rsi", 10.0))
    exit_rsi = float(params.get("exit_rsi", 60.0))
    trend_window = int(params.get("trend_window", 200))
    max_single_position = float(params.get("max_single_position", 0.03))
    closes = [price for _, price in series]
    daily_returns: list[float] = []
    position = 0.0

    for idx in range(1, len(closes)):
        if idx > trend_window + rsi_window:
            rsi = _rsi(closes[idx - rsi_window - 1:idx], rsi_window)
            trend_ma = mean(closes[idx - trend_window:idx])
            if closes[idx - 1] <= trend_ma:
                position = 0.0
            elif rsi <= entry_rsi:
                position = max_single_position
            elif rsi >= exit_rsi:
                position = 0.0
        daily_returns.append(position * _simple_return(closes[idx - 1], closes[idx]))
    return daily_returns


def _mean_reversion_returns(series: list[tuple[str, float]], params: dict[str, Any]) -> list[float]:
    lookback_days = int(params.get("lookback_days", 20))
    entry_z = float(params.get("entry_z", 2.0))
    exit_z = float(params.get("exit_z", 0.5))
    max_single_position = float(params.get("max_single_position", 0.03))
    closes = [price for _, price in series]
    daily_returns: list[float] = []
    position = 0.0

    for idx in range(1, len(closes)):
        if idx >= lookback_days:
            window = closes[idx - lookback_days:idx]
            window_std = pstdev(window)
            z_score = 0.0 if window_std == 0 else (closes[idx - 1] - mean(window)) / window_std
            if z_score <= -entry_z:
                position = max_single_position
            elif z_score >= exit_z:
                position = 0.0
        daily_returns.append(position * _simple_return(closes[idx - 1], closes[idx]))
    return daily_returns


def _backtest_cross_sectional_momentum(price_data: dict[str, list[tuple[str, float]]], params: dict[str, Any]) -> dict[str, Any]:
    aligned = _align_price_data(price_data)
    symbols = sorted(aligned)
    if len(symbols) < 2:
        return {
            "status": "blocked_insufficient_symbols",
            "reason": "Cross-sectional momentum requires at least two symbols",
            "metrics": {},
            "symbols": symbols,
        }

    lookback_days = int(params.get("lookback_days", 252))
    skip_recent_days = int(params.get("skip_recent_days", 21))
    top_fraction = float(params.get("top_fraction", 0.20))
    max_single_position = float(params.get("max_single_position", 0.05))
    dates = _common_dates(aligned)
    daily_returns: list[float] = []

    for offset in range(1, len(dates)):
        signal_idx = offset - 1
        if signal_idx <= lookback_days + skip_recent_days:
            daily_returns.append(0.0)
            continue

        scores = {}
        for symbol in symbols:
            prices = [aligned[symbol][date] for date in dates]
            start = prices[signal_idx - lookback_days - skip_recent_days]
            end = prices[signal_idx - skip_recent_days]
            scores[symbol] = _simple_return(start, end)

        ranked = sorted(scores, key=scores.get, reverse=True)
        top_count = max(1, math.ceil(len(ranked) * top_fraction))
        selected = set(ranked[:top_count])
        weight = min(max_single_position, 1.0 / len(selected))
        period_return = 0.0
        for symbol in selected:
            start = aligned[symbol][dates[offset - 1]]
            end = aligned[symbol][dates[offset]]
            period_return += weight * _simple_return(start, end)
        daily_returns.append(period_return)

    return _result_from_returns("classic_cross_sectional_momentum_v1", symbols, daily_returns)


def _backtest_dual_momentum_rotation(price_data: dict[str, list[tuple[str, float]]], params: dict[str, Any]) -> dict[str, Any]:
    aligned = _align_price_data(price_data)
    symbols = sorted(aligned)
    if len(symbols) < 2:
        return {
            "status": "blocked_insufficient_symbols",
            "reason": "Dual momentum rotation requires at least two symbols",
            "metrics": {},
            "symbols": symbols,
        }

    lookback_days = int(params.get("lookback_days", 126))
    top_n = int(params.get("top_n", 2))
    absolute_momentum_threshold = float(params.get("absolute_momentum_threshold", 0.0))
    max_single_position = float(params.get("max_single_position", 0.05))
    dates = _common_dates(aligned)
    daily_returns: list[float] = []

    for offset in range(1, len(dates)):
        signal_idx = offset - 1
        if signal_idx <= lookback_days:
            daily_returns.append(0.0)
            continue

        scores = {
            symbol: _simple_return(aligned[symbol][dates[signal_idx - lookback_days]], aligned[symbol][dates[signal_idx]])
            for symbol in symbols
        }
        ranked = sorted(scores, key=scores.get, reverse=True)
        selected = [symbol for symbol in ranked[:top_n] if scores[symbol] > absolute_momentum_threshold]
        weight = min(max_single_position, 1.0 / len(selected)) if selected else 0.0
        period_return = sum(
            weight * _simple_return(aligned[symbol][dates[offset - 1]], aligned[symbol][dates[offset]])
            for symbol in selected
        )
        daily_returns.append(period_return)

    return _result_from_returns("advanced_dual_momentum_rotation_v1", symbols, daily_returns)


def _backtest_pairs_trading(price_data: dict[str, list[tuple[str, float]]], params: dict[str, Any]) -> dict[str, Any]:
    aligned = _align_price_data(price_data)
    symbols = sorted(aligned)[:2]
    if len(symbols) < 2:
        return {
            "status": "blocked_insufficient_symbols",
            "reason": "Pairs trading requires at least two symbols",
            "metrics": {},
            "symbols": symbols,
        }

    leg_a, leg_b = symbols
    dates = _common_dates({leg_a: aligned[leg_a], leg_b: aligned[leg_b]})
    lookback_days = int(params.get("lookback_days", 60))
    entry_z = float(params.get("entry_z", 2.0))
    exit_z = float(params.get("exit_z", 0.5))
    max_pair_gross_exposure = float(params.get("max_pair_gross_exposure", 0.05))
    leg_weight = max_pair_gross_exposure / 2
    daily_returns: list[float] = []
    weight_a = 0.0
    weight_b = 0.0

    spreads = [math.log(aligned[leg_a][date]) - math.log(aligned[leg_b][date]) for date in dates]
    for idx in range(1, len(dates)):
        if idx >= lookback_days:
            window = spreads[idx - lookback_days:idx]
            window_std = pstdev(window)
            z_score = 0.0 if window_std == 0 else (spreads[idx - 1] - mean(window)) / window_std
            if z_score >= entry_z:
                weight_a = -leg_weight
                weight_b = leg_weight
            elif z_score <= -entry_z:
                weight_a = leg_weight
                weight_b = -leg_weight
            elif abs(z_score) <= exit_z:
                weight_a = 0.0
                weight_b = 0.0

        return_a = _simple_return(aligned[leg_a][dates[idx - 1]], aligned[leg_a][dates[idx]])
        return_b = _simple_return(aligned[leg_b][dates[idx - 1]], aligned[leg_b][dates[idx]])
        daily_returns.append(weight_a * return_a + weight_b * return_b)

    return _result_from_returns("classic_pairs_trading_v1", symbols, daily_returns)


def _backtest_dynamic_pairs_trading(strategy_id: str, price_data: dict[str, list[tuple[str, float]]], params: dict[str, Any]) -> dict[str, Any]:
    aligned = _align_price_data(price_data)
    symbols = sorted(aligned)[:2]
    if len(symbols) < 2:
        return {
            "status": "blocked_insufficient_symbols",
            "reason": "Dynamic pairs trading requires at least two symbols",
            "metrics": {},
            "symbols": symbols,
        }

    leg_a, leg_b = symbols
    dates = _common_dates({leg_a: aligned[leg_a], leg_b: aligned[leg_b]})
    lookback_days = int(params.get("lookback_days", 60))
    entry_z = float(params.get("entry_z", 2.0))
    exit_z = float(params.get("exit_z", 0.5))
    max_pair_gross_exposure = float(params.get("max_pair_gross_exposure", 0.05))
    leg_weight = max_pair_gross_exposure / 2
    log_a = [math.log(aligned[leg_a][date]) for date in dates]
    log_b = [math.log(aligned[leg_b][date]) for date in dates]
    daily_returns: list[float] = []
    weight_a = 0.0
    weight_b = 0.0

    for idx in range(1, len(dates)):
        if idx >= lookback_days:
            beta = _rolling_beta(log_a[idx - lookback_days:idx], log_b[idx - lookback_days:idx])
            residuals = [a - beta * b for a, b in zip(log_a[idx - lookback_days:idx], log_b[idx - lookback_days:idx])]
            residual_std = pstdev(residuals)
            residual_z = 0.0 if residual_std == 0 else (residuals[-1] - mean(residuals)) / residual_std
            if residual_z >= entry_z:
                weight_a = -leg_weight
                weight_b = leg_weight
            elif residual_z <= -entry_z:
                weight_a = leg_weight
                weight_b = -leg_weight
            elif abs(residual_z) <= exit_z:
                weight_a = 0.0
                weight_b = 0.0

        return_a = _simple_return(aligned[leg_a][dates[idx - 1]], aligned[leg_a][dates[idx]])
        return_b = _simple_return(aligned[leg_b][dates[idx - 1]], aligned[leg_b][dates[idx]])
        daily_returns.append(weight_a * return_a + weight_b * return_b)

    return _result_from_returns(strategy_id, symbols, daily_returns)


def _backtest_residual_stat_arb(price_data: dict[str, list[tuple[str, float]]], params: dict[str, Any]) -> dict[str, Any]:
    market_symbol = str(params.get("market_symbol", "SPY")).upper()
    aligned = _align_price_data(price_data)
    candidates = [symbol for symbol in sorted(aligned) if symbol != market_symbol]
    if market_symbol not in aligned or not candidates:
        return {
            "status": "blocked_insufficient_symbols",
            "reason": "Residual stat arb requires a market proxy and at least one non-market symbol",
            "metrics": {},
            "symbols": sorted(aligned),
        }

    target_symbol = candidates[0]
    dates = _common_dates({market_symbol: aligned[market_symbol], target_symbol: aligned[target_symbol]})
    lookback_days = int(params.get("lookback_days", 60))
    entry_z = float(params.get("entry_z", 2.0))
    exit_z = float(params.get("exit_z", 0.5))
    max_single_position = float(params.get("max_single_position", 0.03))
    target_returns = [
        _simple_return(aligned[target_symbol][dates[idx - 1]], aligned[target_symbol][dates[idx]])
        for idx in range(1, len(dates))
    ]
    market_returns = [
        _simple_return(aligned[market_symbol][dates[idx - 1]], aligned[market_symbol][dates[idx]])
        for idx in range(1, len(dates))
    ]
    daily_returns: list[float] = []
    position = 0.0

    for idx, target_return in enumerate(target_returns):
        if idx >= lookback_days:
            beta = _rolling_beta(target_returns[idx - lookback_days:idx], market_returns[idx - lookback_days:idx])
            residuals = [
                target - beta * market
                for target, market in zip(target_returns[idx - lookback_days:idx], market_returns[idx - lookback_days:idx])
            ]
            residual_std = pstdev(residuals)
            residual_z = 0.0 if residual_std == 0 else (residuals[-1] - mean(residuals)) / residual_std
            if residual_z <= -entry_z:
                position = max_single_position
            elif residual_z >= exit_z:
                position = 0.0
        daily_returns.append(position * target_return)

    return _result_from_returns("advanced_residual_stat_arb_v1", [market_symbol, target_symbol], daily_returns)


def _result_from_returns(strategy_id: str, symbols: list[str], daily_returns: list[float]) -> dict[str, Any]:
    if not daily_returns:
        return {
            "status": "blocked_insufficient_price_history",
            "reason": "Not enough price history to compute returns",
            "metrics": {},
            "symbols": symbols,
        }

    equity = 1.0
    equity_curve = []
    for daily_return in daily_returns:
        equity *= 1 + daily_return
        equity_curve.append(equity)

    avg_return = mean(daily_returns)
    vol = pstdev(daily_returns)
    sharpe = 0.0 if vol == 0 else avg_return / vol * math.sqrt(252)
    cumulative_return = equity - 1
    annualized_return = (equity ** (252 / len(daily_returns))) - 1 if equity > 0 else -1
    annualized_volatility = vol * math.sqrt(252)

    return {
        "status": "completed_local",
        "strategy_id": strategy_id,
        "symbols": symbols,
        "observations": len(daily_returns),
        "metrics": {
            "cumulative_return": round(cumulative_return, 6),
            "annualized_return": round(annualized_return, 6),
            "annualized_volatility": round(annualized_volatility, 6),
            "sharpe": round(sharpe, 6),
            "max_drawdown": round(_max_drawdown(equity_curve), 6),
        },
        "notes": [
            "Local quick backtest only.",
            "No commission, slippage, borrow cost or tax impact was applied.",
            "Results are research diagnostics, not trading approval.",
        ],
    }


def _load_price_data(root_dir: Path) -> dict[str, list[tuple[str, float]]]:
    data: dict[str, list[tuple[str, float]]] = {}
    for relative_dir in PRICE_DIRS:
        data_dir = root_dir / relative_dir
        if not data_dir.exists():
            continue
        for csv_path in data_dir.glob("*.csv"):
            for symbol, rows in _read_price_csv(csv_path).items():
                data.setdefault(symbol, []).extend(rows)

    return {
        symbol: sorted(set(rows), key=lambda item: item[0])
        for symbol, rows in data.items()
        if len(rows) >= 2
    }


def _read_price_csv(csv_path: Path) -> dict[str, list[tuple[str, float]]]:
    output: dict[str, list[tuple[str, float]]] = {}
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return output
        lower_fields = {field.lower(): field for field in reader.fieldnames}
        date_field = _first_present(lower_fields, ("date", "timestamp", "time", "t"))
        close_field = _first_present(lower_fields, ("close", "adjusted_close", "adj_close", "c"))
        symbol_field = _first_present(lower_fields, ("symbol", "ticker"))
        if not date_field or not close_field:
            return output

        default_symbol = csv_path.stem.upper()
        for row in reader:
            try:
                close = float(row[close_field])
            except (TypeError, ValueError):
                continue
            symbol = (row.get(symbol_field) if symbol_field else default_symbol) or default_symbol
            output.setdefault(symbol.upper(), []).append((str(row[date_field]), close))
    return output


def _load_strategy_params(root_dir: Path, strategy_id: str) -> dict[str, Any]:
    params_path = root_dir / "persistent" / "strategies" / strategy_id / "params.yaml"
    if not params_path.exists():
        return {}
    return _parse_simple_yaml(params_path.read_text(encoding="utf-8"))


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    try:
        import yaml

        parsed = yaml.safe_load(text) or {}
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        result: dict[str, Any] = {}
        parent_key: str | None = None
        for raw_line in text.splitlines():
            if not raw_line.strip() or raw_line.lstrip().startswith("#"):
                continue
            if raw_line.startswith("  ") and parent_key:
                key, value = raw_line.strip().split(":", 1)
                result.setdefault(parent_key, {})[key] = _coerce_scalar(value.strip())
                continue
            key, _, value = raw_line.partition(":")
            if not value.strip():
                parent_key = key.strip()
                result[parent_key] = {}
            else:
                parent_key = None
                result[key.strip()] = _coerce_scalar(value.strip())
        return result


def _coerce_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _align_price_data(price_data: dict[str, list[tuple[str, float]]]) -> dict[str, dict[str, float]]:
    return {
        symbol: {date: price for date, price in rows}
        for symbol, rows in price_data.items()
    }


def _common_dates(aligned: dict[str, dict[str, float]]) -> list[str]:
    common: set[str] | None = None
    for rows in aligned.values():
        dates = set(rows)
        common = dates if common is None else common & dates
    return sorted(common or set())


def _simple_return(start: float, end: float) -> float:
    if start == 0:
        return 0.0
    return end / start - 1


def _annualized_volatility(returns: list[float]) -> float:
    if not returns:
        return 0.0
    return pstdev(returns) * math.sqrt(252)


def _rolling_beta(y_values: list[float], x_values: list[float]) -> float:
    if len(y_values) != len(x_values) or not y_values:
        return 1.0
    x_mean = mean(x_values)
    y_mean = mean(y_values)
    variance = sum((x - x_mean) ** 2 for x in x_values)
    if variance == 0:
        return 1.0
    covariance = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    return covariance / variance


def _rsi(prices: list[float], window: int) -> float:
    if len(prices) < window + 1:
        return 50.0
    gains = []
    losses = []
    for idx in range(1, len(prices)):
        change = prices[idx] - prices[idx - 1]
        gains.append(max(change, 0.0))
        losses.append(abs(min(change, 0.0)))
    avg_gain = mean(gains[-window:])
    avg_loss = mean(losses[-window:])
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _max_drawdown(equity_curve: list[float]) -> float:
    peak = 1.0
    max_drawdown = 0.0
    for value in equity_curve:
        peak = max(peak, value)
        if peak:
            max_drawdown = min(max_drawdown, value / peak - 1)
    return max_drawdown


def _first_present(fields: dict[str, str], names: tuple[str, ...]) -> str | None:
    for name in names:
        if name in fields:
            return fields[name]
    return None


def _review_text(strategy_id: str, results: dict[str, Any]) -> str:
    if results["status"] == "completed_local":
        metrics = results["metrics"]
        return (
            f"Local quick backtest completed for {strategy_id}.\n\n"
            f"- Sharpe: {metrics['sharpe']}\n"
            f"- Cumulative return: {metrics['cumulative_return']}\n"
            f"- Max drawdown: {metrics['max_drawdown']}\n\n"
            "This is not a promotion or trading approval.\n"
        )
    return (
        f"Backtest not completed for {strategy_id}.\n\n"
        f"- Status: {results['status']}\n"
        f"- Reason: {results.get('reason', 'not specified')}\n"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("strategy_id", nargs="?", default="example_ma_cross_v1")
    args = parser.parse_args()
    print(json.dumps(run(args.strategy_id), indent=2))
