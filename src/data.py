from pathlib import Path
import time
import random

import akshare as ak
import pandas as pd


ETF_NAMES = {
    "510300": "沪深300ETF",
    "511010": "国债ETF",
    "518880": "黄金ETF",
    "513100": "纳指ETF",
    "159920": "恒生ETF",
}

START_DATE = "20150101"
END_DATE = "20251231"

# 每次远程请求至少间隔 20 秒，实际间隔为 20~35 秒。
# 五只 ETF 首次下载大约需要 2~3 分钟。
MIN_REQUEST_INTERVAL_SECONDS = 30
MAX_REQUEST_JITTER_SECONDS = 30

MAX_RETRIES = 1
RETRY_WAIT_SECONDS = (300, )

_last_request_time = None


def wait_for_rate_limit():
    """在远程请求之间保留较长间隔，避免连续请求数据接口。"""
    global _last_request_time

    now = time.monotonic()

    if _last_request_time is not None:
        elapsed = now - _last_request_time
        wait_seconds = (
            MIN_REQUEST_INTERVAL_SECONDS
            + random.uniform(0, MAX_REQUEST_JITTER_SECONDS)
            - elapsed
        )

        if wait_seconds > 0:
            print(f"等待 {wait_seconds:.1f} 秒后请求")
            time.sleep(wait_seconds)

    # 记录真正发出请求前的时间
    _last_request_time = time.monotonic()


def download_etf_data(
    symbol,
    start_date=START_DATE,
    end_date=END_DATE,
):
    """低频下载单只 ETF；失败后长时间退避。"""
    last_error = None

    for attempt in range(MAX_RETRIES):
        wait_for_rate_limit()

        try:
            print(
                f"请求数据：{symbol}，"
                f"第 {attempt + 1}/{MAX_RETRIES} 次尝试"
            )

            data = ak.fund_etf_hist_em(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq",
            )

            if data.empty:
                raise RuntimeError(f"{symbol} 返回空数据")

            return data

        except Exception as error:
            last_error = error
            print(f"{symbol} 请求失败：{error}")

            if attempt < MAX_RETRIES - 1:
                retry_wait = RETRY_WAIT_SECONDS[attempt]
                print(f"暂停 {retry_wait} 秒后再尝试")
                time.sleep(retry_wait)

    raise RuntimeError(
        f"{symbol} 连续 {MAX_RETRIES} 次获取失败，请稍后手动重试。"
    ) from last_error


def validate_etf_data(data, symbol):
    """检查并整理单只 ETF 的原始数据。"""
    required_columns = {"日期", "收盘"}
    missing_columns = required_columns - set(data.columns)

    if missing_columns:
        raise ValueError(
            f"{symbol} 缺少必要字段：{missing_columns}"
        )

    data = data.copy()
    data["日期"] = pd.to_datetime(data["日期"])
    data["收盘"] = pd.to_numeric(
        data["收盘"],
        errors="coerce",
    )
    data = data.sort_values("日期")

    duplicate_count = data["日期"].duplicated().sum()

    if duplicate_count > 0:
        raise ValueError(
            f"{symbol} 存在 {duplicate_count} 个重复日期"
        )

    missing_close_count = data["收盘"].isna().sum()

    if missing_close_count > 0:
        raise ValueError(
            f"{symbol} 存在 {missing_close_count} 个缺失收盘价"
        )

    non_positive_count = (data["收盘"] <= 0).sum()

    if non_positive_count > 0:
        raise ValueError(
            f"{symbol} 存在 {non_positive_count} 个非正收盘价"
        )

    return data


def fetch_or_load_etf(
    symbol,
    start_date=START_DATE,
    end_date=END_DATE,
    cache_dir="data/raw",
):
    """优先读取缓存；缓存不存在时限速下载并保存。"""
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)

    cache_file = cache_path / f"{symbol}.csv"

    if cache_file.exists():
        print(f"读取本地缓存：{cache_file}")

        data = pd.read_csv(
            cache_file,
            parse_dates=["日期"],
        )
    else:
        data = download_etf_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )

        data = validate_etf_data(data, symbol)

        data.to_csv(
            cache_file,
            index=False,
            encoding="utf-8-sig",
        )

        print(f"已保存本地缓存：{cache_file}")

    return validate_etf_data(data, symbol)


def load_price_table():
    """读取五只 ETF，返回日期为索引、ETF 名称为列的价格宽表。"""
    price_series = {}
    summary_rows = []

    for symbol, name in ETF_NAMES.items():
        data = fetch_or_load_etf(symbol)

        price_series[name] = (
            data.set_index("日期")["收盘"]
        )

        summary_rows.append({
            "代码": symbol,
            "名称": name,
            "观测数量": len(data),
            "起始日期": data["日期"].min(),
            "结束日期": data["日期"].max(),
            "缺失收盘价": data["收盘"].isna().sum(),
            "重复日期": data["日期"].duplicated().sum(),
            "非正收盘价": (data["收盘"] <= 0).sum(),
        })

    prices = pd.DataFrame(price_series).sort_index()
    summary = pd.DataFrame(summary_rows)

    return prices, summary