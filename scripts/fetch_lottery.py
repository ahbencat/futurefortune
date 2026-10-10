#!/usr/bin/env python3
"""
排列3/排列5 历史数据抓取脚本
数据源：江苏体彩网 https://www.js-lottery.com

用法:
    python scripts/fetch_lottery.py --type p3          # 抓取排列3
    python scripts/fetch_lottery.py --type p5          # 抓取排列5
    python scripts/fetch_lottery.py --type p3 --update # 增量更新排列3
    python scripts/fetch_lottery.py --type p5 --update # 增量更新排列5
"""

import argparse
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from lottery_common import data_path, load_existing, merge_data, save_data, print_summary

BASE_URL = "https://www.js-lottery.com/Lottery/_ListData"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

# 每种彩票对应的 Referer 和输出文件
LOTTERY_CONFIG = {
    "p3": {
        "name": "排列3",
        "referer": "https://www.js-lottery.com/wfzq/p3p5/p3data",
        "output": "pl3_all_data.json",
        "digits": 3,
    },
    "p5": {
        "name": "排列5",
        "referer": "https://www.js-lottery.com/wfzq/p3p5/p5data",
        "output": "pl5_all_data.json",
        "digits": 5,
    },
}

# HTML 解析正则
PATTERN = re.compile(
    r'<td style="text-align:center;">(\d{4}-\d{2}-\d{2})</td>\s*'
    r'<td style="text-align:center;">(\d+)</td>\s*'
    r'<td style="text-align:center;">\s*([\d\s]+)\s*</td>'
)


def fetch_page(item_type: str, referer: str, page: int, retries: int = 3) -> list:
    """抓取单页数据"""
    headers = {**HEADERS, "Referer": referer}
    params = {"itemType": item_type, "pageindex": str(page), "size": "10"}

    for attempt in range(retries):
        try:
            resp = requests.get(BASE_URL, params=params, headers=headers, timeout=15)
            if resp.status_code == 200:
                return [
                    {"date": m[0], "issue_no": m[1], "numbers": m[2].strip().split()}
                    for m in PATTERN.findall(resp.text)
                ]
            else:
                print(f"  第 {page} 页状态码 {resp.status_code}，重试 {attempt + 1}/{retries}")
        except Exception as e:
            print(f"  第 {page} 页异常: {e}，重试 {attempt + 1}/{retries}")
        time.sleep(1 + attempt)

    return []


def fetch_all(item_type: str, referer: str, total_pages: int, workers: int = 10) -> list:
    """并发抓取全部数据"""
    all_data = []
    failed_pages = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_page = {
            executor.submit(fetch_page, item_type, referer, page): page
            for page in range(1, total_pages + 1)
        }

        done = 0
        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                page_data = future.result()
                if page_data:
                    all_data.extend(page_data)
                else:
                    failed_pages.append(page)
            except Exception as e:
                print(f"  第 {page} 页错误: {e}")
                failed_pages.append(page)

            done += 1
            if done % 100 == 0:
                print(f"  进度 {done}/{total_pages} 页，累计 {len(all_data)} 条")

    # 重试失败的页
    if failed_pages:
        print(f"  重试 {len(failed_pages)} 个失败页...")
        for page in failed_pages:
            page_data = fetch_page(item_type, referer, page, retries=5)
            all_data.extend(page_data)

    all_data.sort(key=lambda x: int(x["issue_no"]))
    return all_data


def get_total_pages(item_type: str, referer: str) -> int:
    """探测总页数"""
    headers = {**HEADERS, "Referer": referer}
    params = {"itemType": item_type, "pageindex": "1", "size": "10"}

    resp = requests.get(BASE_URL, params=params, headers=headers, timeout=15)
    # 从分页信息中提取总页数
    match = re.search(r'共\s*(\d+)\s*页', resp.text)
    if match:
        return int(match.group(1))

    # 备选：通过总条数计算
    match = re.search(r'共\s*(\d+)\s*条', resp.text)
    if match:
        return (int(match.group(1)) + 9) // 10

    # 如果都找不到，用二分法探测
    print("  无法从页面获取总页数，使用探测方式...")
    low, high = 1, 2000
    while low < high:
        mid = (low + high + 1) // 2
        params["pageindex"] = str(mid)
        resp = requests.get(BASE_URL, params=params, headers=headers, timeout=15)
        if PATTERN.search(resp.text):
            low = mid
        else:
            high = mid - 1
        time.sleep(0.1)
    return low


def main():
    parser = argparse.ArgumentParser(description="排列3/排列5 历史数据抓取")
    parser.add_argument("--type", required=True, choices=["p3", "p5"], help="彩票类型")
    parser.add_argument("--update", action="store_true", help="增量更新模式")
    parser.add_argument("--pages", type=int, default=None, help="指定总页数（跳过探测）")
    parser.add_argument("--workers", type=int, default=10, help="并发线程数")
    args = parser.parse_args()

    config = LOTTERY_CONFIG[args.type]
    output_file = data_path(config["output"])

    print(f"=== {config['name']} 数据抓取 ===")
    print(f"类型: {args.type}")
    print(f"输出: {output_file}")

    # 增量更新：加载已有数据
    existing_data = []
    if args.update:
        existing_data = load_existing(output_file)
        if existing_data:
            print(f"已有数据: {len(existing_data)} 条")

    # 探测总页数
    if args.pages:
        total_pages = args.pages
    else:
        print("  探测总页数...")
        total_pages = get_total_pages(args.type, config["referer"])
    print(f"  总页数: {total_pages}")

    # 抓取数据
    print(f"  开始抓取（{args.workers} 线程并发）...")
    all_data = fetch_all(args.type, config["referer"], total_pages, args.workers)

    # 合并去重
    all_data, added = merge_data(existing_data, all_data)
    if existing_data:
        print(f"  新增 {added} 条")

    save_data(output_file, all_data)
    print_summary(all_data)


if __name__ == "__main__":
    main()
