#!/usr/bin/env python3
"""
双色球历史数据抓取脚本
数据源：500.com datachart（参考 yangxb919/lottery-data 的方法）

用法:
    python scripts/fetch_ssq.py            # 全量抓取
    python scripts/fetch_ssq.py --update   # 增量更新
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime

import requests

# 仓库根目录
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = "datas"
OUTPUT = "ssq_all_data.json"

# 500.com datachart 接口
URL = "https://datachart.500.com/ssq/history/newinc/history.php"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Referer": "https://www.500.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def data_path(filename: str) -> str:
    return os.path.join(REPO_ROOT, DATA_DIR, filename)


def load_existing(path: str) -> list:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_data(path: str, data: list):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch_html(start_issue: str, end_issue: str, retries: int = 3) -> str:
    """抓取 500.com datachart 页面"""
    params = {"start": start_issue, "end": end_issue}
    for attempt in range(retries):
        try:
            resp = requests.get(URL, params=params, headers=HEADERS, timeout=40)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            if "tdata" not in resp.text:
                raise ValueError("response missing tbody#tdata")
            return resp.text
        except Exception as e:
            print(f"  抓取失败: {e}，重试 {attempt + 1}/{retries}")
            time.sleep(2 * attempt)
    raise RuntimeError(f"failed to fetch: {start_issue}-{end_issue}")


def parse_rows(html: str) -> list:
    """解析 HTML 表格，返回项目格式数据"""
    # 找 tbody#tdata 区域
    tdata_match = re.search(r'<tbody[^>]*id="tdata"[^>]*>(.*?)</tbody>', html, re.DOTALL)
    if not tdata_match:
        raise ValueError("未找到 tbody#tdata")

    tdata = tdata_match.group(1)
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tdata, re.DOTALL)

    records = []
    for row in rows:
        cols = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        cols_clean = [re.sub(r'<[^>]+>', '', c).strip().replace('\xa0', '') for c in cols]

        if len(cols_clean) < 10:
            continue

        # 期号（5位 YYNNN -> 转为7位 YYYYNNN）
        issue_5 = cols_clean[1]
        if not re.fullmatch(r'\d{5}', issue_5):
            continue
        issue = f"20{issue_5}"

        # 日期（最后一列）
        date = cols_clean[-1]
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date):
            continue

        # 红球（列2-7），蓝球（列8）
        try:
            red = [f"{int(cols_clean[i]):02d}" for i in range(2, 8)]
            blue = f"{int(cols_clean[8]):02d}"
        except (ValueError, IndexError):
            continue

        # 验证范围
        red_nums = [int(r) for r in red]
        blue_num = int(blue)
        if len(set(red_nums)) != 6 or not all(1 <= n <= 33 for n in red_nums):
            continue
        if not (1 <= blue_num <= 16):
            continue

        records.append({
            "date": date,
            "issue_no": issue,
            "front": red,
            "back": [blue],
        })

    return records


def merge_data(existing: list, new_items: list) -> tuple:
    """按 issue_no 合并去重（新覆盖旧），按期号升序"""
    merged = {}
    for item in list(existing) + list(new_items):
        merged[item["issue_no"]] = item
    result = sorted(merged.values(), key=lambda x: int(x["issue_no"]))
    added = len(result) - len({item["issue_no"] for item in existing})
    return result, added


def print_summary(data: list):
    print(f"\n完成! 共 {len(data)} 条")
    if data:
        print(f"期号范围: {data[0]['issue_no']} - {data[-1]['issue_no']}")
        print(f"日期范围: {data[0]['date']} - {data[-1]['date']}")


def main():
    parser = argparse.ArgumentParser(description="双色球历史数据抓取")
    parser.add_argument("--update", action="store_true", help="增量更新模式")
    parser.add_argument("--start", default="03001", help="起始期号（默认 03001）")
    parser.add_argument("--end", default=None, help="结束期号（默认当年 YY200）")
    args = parser.parse_args()

    output_file = data_path(OUTPUT)
    print("=== 双色球 数据抓取 ===")
    print(f"数据源: {URL}")
    print(f"输出: {output_file}")

    # 结束期号：默认当年 YY200
    if args.end:
        end_issue = args.end
    else:
        end_issue = f"{datetime.now().year % 100:02d}200"

    existing_data = load_existing(output_file)
    if existing_data:
        print(f"已有数据: {len(existing_data)} 条")

    # 增量模式：只抓最近几期
    if args.update and existing_data:
        latest_issue = existing_data[-1]["issue_no"]  # 7位 YYYYNNN
        # 转为5位 YYNNN 格式给 API
        latest_5 = latest_issue[2:]  # 去掉前两位年份
        start_5 = f"{int(latest_5) - 1:05d}"
        start_issue = start_5
        print(f"  增量抓取: {start_issue} -> {end_issue}")
    else:
        start_issue = args.start
        print(f"  全量抓取: {start_issue} -> {end_issue}")

    html = fetch_html(start_issue, end_issue)
    fresh = parse_rows(html)
    print(f"  解析到 {len(fresh)} 条")

    all_data, added = merge_data(existing_data, fresh)
    if existing_data:
        print(f"  新增 {added} 条")

    save_data(output_file, all_data)
    print_summary(all_data)


if __name__ == "__main__":
    main()
