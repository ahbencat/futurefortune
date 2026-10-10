#!/usr/bin/env python3
"""
彩票数据抓取的公共函数：读写 JSON、合并去重、修正、增量抓取、摘要输出。

各彩种的抓取脚本（fetch_lottery.py / fetch_dlt.py）负责各自的配置与字段转换，
取数与落盘统一走这里。
"""

import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

# 仓库根目录（scripts/ 的上一级）
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------- 江苏体彩网 www.js-lottery.com 通用抓取 ----------
# 排列三/排列五（itemType=p3/p5）与超级大乐透（itemType=lo）共用同一接口与表格结构

LIST_URL = "https://www.js-lottery.com/Lottery/_ListData"

LIST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

# 表格三列：发布日期 / 期号 / 开奖号码（第 4 列「详细」链接不参与匹配）
LIST_PATTERN = re.compile(
    r'<td style="text-align:center;">(\d{4}-\d{2}-\d{2})</td>\s*'
    r'<td style="text-align:center;">(\d+)</td>\s*'
    r'<td style="text-align:center;">\s*([\d\s]+)\s*</td>'
)


def fetch_list_page(item_type: str, referer: str, page: int, size: int = 10,
                    retries: int = 3):
    """
    抓取一页开奖数据，返回 [{date, issue_no, numbers: [...]}]。
    请求失败返回 None（区别于「成功但该页无数据」的空列表）。
    """
    headers = {**LIST_HEADERS, "Referer": referer}
    params = {"itemType": item_type, "pageindex": str(page), "size": str(size)}

    for attempt in range(retries):
        try:
            resp = requests.get(LIST_URL, params=params, headers=headers, timeout=15)
            if resp.status_code == 200:
                return [
                    {"date": m[0], "issue_no": m[1], "numbers": m[2].strip().split()}
                    for m in LIST_PATTERN.findall(resp.text)
                ]
            print(f"  第 {page} 页状态码 {resp.status_code}，重试 {attempt + 1}/{retries}")
        except Exception as e:
            print(f"  第 {page} 页异常: {e}，重试 {attempt + 1}/{retries}")
        time.sleep(1 + attempt)

    return None


def get_total_pages(item_type: str, referer: str) -> int:
    """探测总页数"""
    headers = {**LIST_HEADERS, "Referer": referer}
    params = {"itemType": item_type, "pageindex": "1", "size": "10"}

    resp = requests.get(LIST_URL, params=params, headers=headers, timeout=15)
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
        resp = requests.get(LIST_URL, params=params, headers=headers, timeout=15)
        if LIST_PATTERN.search(resp.text):
            low = mid
        else:
            high = mid - 1
        time.sleep(0.1)
    return low


def fetch_all_pages(item_type: str, referer: str, total_pages: int, workers: int = 10) -> list:
    """并发抓取全部页"""
    all_data = []
    failed_pages = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_page = {
            executor.submit(fetch_list_page, item_type, referer, page): page
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
            page_data = fetch_list_page(item_type, referer, page, retries=5)
            if page_data:
                all_data.extend(page_data)

    all_data.sort(key=lambda x: int(x["issue_no"]))
    return all_data


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
        if rows is None:
            # 抓取失败：必须区别于「已追平」，否则会静默假装成功
            print(f"  增量抓取: 第 {page} 页抓取失败")
            return collected, False
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
