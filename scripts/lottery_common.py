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


def fetch_incremental(fetch_page, known_issues: set, key: str = "issue_no",
                      max_pages: int = 50) -> tuple:
    """
    增量抓取：从最新页开始逐页取，直到某页的期号全部已存在（已追平）为止。

    fetch_page(page) 返回该页记录列表，要求页序「最新在前」。
    返回 (抓取到的记录, 是否追平)。未追平说明达到页数上限，应改用全量抓取。
    """
    collected = []
    for page in range(1, max_pages + 1):
        rows = fetch_page(page)
        if not rows:
            print(f"  增量抓取: 第 {page} 页无数据，结束")
            return collected, True
        collected.extend(rows)
        if all(row[key] in known_issues for row in rows):
            print(f"  增量抓取: 第 {page} 页已全部存在，追平（共取 {len(collected)} 条）")
            return collected, True
        print(f"  增量抓取: 第 {page} 页含新增，继续翻页...")
    return collected, False


def load_patches() -> dict:
    """加载数据修正表 scripts/data_patches.json"""
    path = os.path.join(REPO_ROOT, "scripts", "data_patches.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def apply_patches(data: list, lottery: str) -> list:
    """
    应用数据修正（每天重新抓取会覆盖源数据，故修正放在流水线里而非直接改文件）。

    fixes: 按期号修正字段；extra: 补充数据源缺失的期号。
    """
    patches = load_patches().get(lottery) or {}
    fixes = patches.get("fixes") or {}
    extra = patches.get("extra") or []
    if not fixes and not extra:
        return data

    by_issue = {item["issue_no"]: item for item in data}
    fixed = 0
    added = 0

    for issue, fields in fixes.items():
        item = by_issue.get(issue)
        if item is None:
            continue
        for key, value in fields.items():
            if item.get(key) != value:
                item[key] = value
                fixed += 1

    for item in extra:
        if item["issue_no"] not in by_issue:
            by_issue[item["issue_no"]] = item
            added += 1

    print(f"  数据修正: 修改 {fixed} 处，补充 {added} 期")
    return sorted(by_issue.values(), key=lambda x: int(x["issue_no"]))


def print_summary(data: list):
    """打印期数、期号与日期范围"""
    print(f"\n完成! 共 {len(data)} 条")
    if data:
        print(f"期号范围: {data[0]['issue_no']} - {data[-1]['issue_no']}")
        print(f"日期范围: {data[0]['date']} - {data[-1]['date']}")
