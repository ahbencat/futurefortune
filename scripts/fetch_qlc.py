#!/usr/bin/env python3
"""
七乐彩历史数据抓取脚本
数据源：500.com kaijiang XML 接口

用法:
    python scripts/fetch_qlc.py            # 全量抓取
    python scripts/fetch_qlc.py --update   # 增量更新
"""

import argparse
import json
import os
import re
import time
from datetime import datetime

import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = "datas"
OUTPUT = "qlc_all_data.json"

# 500.com 七乐彩开奖 XML 接口
URL = "https://www.500.com/static/info/kaijiang/xml/qlc/list.xml"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.500.com/",
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


def fetch_xml(retries: int = 3) -> str:
    """抓取 500.com 七乐彩 XML 数据"""
    for attempt in range(retries):
        try:
            resp = requests.get(URL, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            return resp.text
        except Exception as e:
            print(f"  抓取失败: {e}，重试 {attempt + 1}/{retries}")
            time.sleep(2 * attempt)
    raise RuntimeError("failed to fetch qlc xml")


def parse_xml(xml_text: str) -> list:
    """解析 XML，返回项目格式数据"""
    rows = re.findall(
        r'<row\s+expect="(\d+)"\s+opencode="([^"]*)"\s+opentime="([^"]*)"', xml_text
    )

    records = []
    for expect, opencode, opentime in rows:
        # opencode 格式: "06,08,14,17,19,23,26|28" （7正选|1特选）
        if "|" not in opencode:
            continue
        front_str, back_str = opencode.split("|", 1)
        front = [n.strip().zfill(2) for n in front_str.split(",")]
        back = [back_str.strip().zfill(2)]

        # 验证
        if len(front) != 7:
            continue
        front_nums = [int(n) for n in front]
        if len(set(front_nums)) != 7 or not all(1 <= n <= 30 for n in front_nums):
            continue
        if not (1 <= int(back[0]) <= 30):
            continue

        # 期号 5位 YYNNN -> 7位 YYYYNNN
        issue = f"20{expect}" if len(expect) == 5 else expect
        date = opentime.split(" ")[0] if " " in opentime else opentime

        records.append({
            "date": date,
            "issue_no": issue,
            "front": front,
            "back": back,
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
    parser = argparse.ArgumentParser(description="七乐彩历史数据抓取")
    parser.add_argument("--update", action="store_true", help="增量更新模式")
    args = parser.parse_args()

    output_file = data_path(OUTPUT)
    print("=== 七乐彩 数据抓取 ===")
    print(f"数据源: {URL}")
    print(f"输出: {output_file}")

    existing_data = load_existing(output_file)
    if existing_data:
        print(f"已有数据: {len(existing_data)} 条")

    xml_text = fetch_xml()
    fresh = parse_xml(xml_text)
    print(f"  解析到 {len(fresh)} 条")

    all_data, added = merge_data(existing_data, fresh)
    if existing_data:
        print(f"  新增 {added} 条")

    save_data(output_file, all_data)
    print_summary(all_data)


if __name__ == "__main__":
    main()
