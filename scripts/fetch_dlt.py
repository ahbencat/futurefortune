#!/usr/bin/env python3
"""
超级大乐透历史数据抓取脚本
数据源：中国体彩网开放接口 https://webapi.sporttery.cn

用法:
    python scripts/fetch_dlt.py            # 全量抓取
    python scripts/fetch_dlt.py --update   # 增量更新
"""

import argparse
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

from lottery_common import data_path, load_existing, merge_data, save_data, print_summary

API_URL = ("https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry"
           "?gameNo=85&provinceId=0&pageSize={size}&isVerify=1&pageNo={page}")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://static.sporttery.cn/",
}

PAGE_SIZE = 100
OUTPUT = "dlt_all_data.json"


def fetch_page(page: int, retries: int = 3) -> dict:
    """抓取单页，返回接口的 value 字段（失败返回空字典）"""
    url = API_URL.format(size=PAGE_SIZE, page=page)

    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            if payload.get("success"):
                return payload["value"]
            print(f"  第 {page} 页返回失败: {payload.get('errorMessage')}，重试 {attempt + 1}/{retries}")
        except Exception as e:
            print(f"  第 {page} 页异常: {e}，重试 {attempt + 1}/{retries}")
        time.sleep(1 + attempt)

    return {}


def parse_row(row: dict) -> dict:
    """接口记录 -> {date, issue_no, front(前区5个), back(后区2个)}"""
    numbers = row["lotteryDrawResult"].split()
    return {
        "date": row["lotteryDrawTime"],
        "issue_no": row["lotteryDrawNum"],
        "front": numbers[:5],
        "back": numbers[5:],
    }


def fetch_all(total_pages: int, workers: int = 5) -> list:
    """并发抓取第 2 页起的所有页（第 1 页由 main 先行抓取用于探测页数）"""
    rows = []
    failed_pages = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_page = {
            executor.submit(fetch_page, page): page
            for page in range(2, total_pages + 1)
        }

        done = 1
        for future in as_completed(future_to_page):
            page = future_to_page[future]
            value = future.result()
            if value:
                rows.extend(value.get("list") or [])
            else:
                failed_pages.append(page)

            done += 1
            if done % 5 == 0:
                print(f"  进度 {done}/{total_pages} 页，累计 {len(rows)} 条")

    # 重试失败的页
    if failed_pages:
        print(f"  重试 {len(failed_pages)} 个失败页...")
        for page in failed_pages:
            value = fetch_page(page, retries=5)
            rows.extend(value.get("list") or [])

    return rows


def main():
    parser = argparse.ArgumentParser(description="超级大乐透历史数据抓取")
    parser.add_argument("--update", action="store_true", help="增量更新模式")
    parser.add_argument("--workers", type=int, default=5, help="并发线程数")
    args = parser.parse_args()

    output_file = data_path(OUTPUT)

    print("=== 超级大乐透 数据抓取 ===")
    print(f"输出: {output_file}")

    # 增量更新：加载已有数据
    existing_data = []
    if args.update:
        existing_data = load_existing(output_file)
        if existing_data:
            print(f"已有数据: {len(existing_data)} 条")

    # 首页用于探测总页数
    first = fetch_page(1)
    if not first:
        print("首页抓取失败，退出")
        return

    total_pages = first.get("pages") or 1
    print(f"  总期数: {first.get('total')}，总页数: {total_pages}")

    rows = list(first.get("list") or [])
    print(f"  开始抓取（{args.workers} 线程并发）...")
    rows.extend(fetch_all(total_pages, args.workers))

    all_data = [parse_row(row) for row in rows]

    # 合并去重
    all_data, added = merge_data(existing_data, all_data)
    if existing_data:
        print(f"  新增 {added} 条")

    save_data(output_file, all_data)
    print_summary(all_data)


if __name__ == "__main__":
    main()
