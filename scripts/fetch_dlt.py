#!/usr/bin/env python3
"""
超级大乐透历史数据抓取脚本
数据源：江苏体彩网 https://www.js-lottery.com（itemType=lo，与排列五同站同接口）

说明：官方接口 webapi.sporttery.cn 对境外 IP 返回 HTTP 567，GitHub Actions
（境外 runner）无法访问，故改用江苏体彩网。该源缺少最早的 07001-07004 期，
且 16003/16004 日期有误，均由 scripts/data_patches.json 修正。

用法:
    python scripts/fetch_dlt.py            # 全量抓取
    python scripts/fetch_dlt.py --update   # 增量更新
"""

import argparse
import sys

from lottery_common import (apply_patches, data_path, fetch_all_pages, fetch_incremental,
                            fetch_list_page, get_total_pages, load_existing, merge_data,
                            print_summary, save_data)

ITEM_TYPE = "lo"
REFERER = "https://www.js-lottery.com/wfzq/dlt/data"
OUTPUT = "dlt_all_data.json"


def to_dlt(item: dict) -> dict:
    """江苏体彩网记录（7 个号码）-> {date, issue_no, front(前区5), back(后区2)}"""
    return {
        "date": item["date"],
        "issue_no": item["issue_no"],
        "front": item["numbers"][:5],
        "back": item["numbers"][5:],
    }


def main():
    parser = argparse.ArgumentParser(description="超级大乐透历史数据抓取")
    parser.add_argument("--update", action="store_true", help="增量更新模式")
    parser.add_argument("--pages", type=int, default=None, help="指定总页数（跳过探测）")
    parser.add_argument("--workers", type=int, default=10, help="并发线程数")
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

    # 抓取数据
    if existing_data:
        # 增量：从最新页开始，追平已有数据即停止（通常 1-2 页）
        known = {item["issue_no"] for item in existing_data}
        print("  增量抓取（最新页起，追平后停止）...")
        raw, caught_up = fetch_incremental(
            lambda page: fetch_list_page(ITEM_TYPE, REFERER, page), known)
        if not caught_up:
            print("  错误: 抓取失败或未追平，本次不更新数据")
            sys.exit(1)
    else:
        # 全量：探测总页数后并发抓取
        if args.pages:
            total_pages = args.pages
        else:
            print("  探测总页数...")
            total_pages = get_total_pages(ITEM_TYPE, REFERER)
        print(f"  总页数: {total_pages}")
        print(f"  开始抓取（{args.workers} 线程并发）...")
        raw = fetch_all_pages(ITEM_TYPE, REFERER, total_pages, args.workers)

    all_data = [to_dlt(item) for item in raw]

    # 合并去重
    all_data, added = merge_data(existing_data, all_data)
    if existing_data:
        print(f"  新增 {added} 条")

    # 应用数据修正（源站缺失的最早期号与错误日期，见 scripts/data_patches.json）
    all_data = apply_patches(all_data, "dlt")

    save_data(output_file, all_data)
    print_summary(all_data)


if __name__ == "__main__":
    main()
