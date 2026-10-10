#!/usr/bin/env python3
"""
彩票数据抓取的公共函数：读写 JSON、合并去重、摘要输出。

各彩种的抓取脚本（fetch_lottery.py / fetch_dlt.py）负责各自的取数逻辑，
数据落盘与合并统一走这里。
"""

import json
import os

# 仓库根目录（scripts/ 的上一级）
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def data_path(filename: str) -> str:
    """仓库根目录下的数据文件路径"""
    return os.path.join(REPO_ROOT, filename)


def load_existing(path: str) -> list:
    """加载已有数据，文件不存在时返回空列表"""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def merge_data(existing: list, new_items: list, key: str = "issue_no") -> tuple:
    """
    按 key 合并去重（后出现的覆盖先出现的），并按期号升序排序。

    返回 (合并后的列表, 新增条数)。
    """
    merged = {}
    for item in list(existing) + list(new_items):
        merged[item[key]] = item

    result = sorted(merged.values(), key=lambda x: int(x[key]))
    added = len(result) - len({item[key] for item in existing})
    return result, added


def save_data(path: str, data: list):
    """写入 JSON 数据文件"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_summary(data: list):
    """打印期数、期号与日期范围"""
    print(f"\n完成! 共 {len(data)} 条")
    if data:
        print(f"期号范围: {data[0]['issue_no']} - {data[-1]['issue_no']}")
        print(f"日期范围: {data[0]['date']} - {data[-1]['date']}")
