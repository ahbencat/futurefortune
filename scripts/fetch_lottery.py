#!/usr/bin/env python3
"""
排列3/排列5/7星彩 历史数据抓取脚本
数据源：江苏体彩网 https://www.js-lottery.com

用法:
    python scripts/fetch_lottery.py --type p3          # 抓取排列3
    python scripts/fetch_lottery.py --type p5          # 抓取排列5
    python scripts/fetch_lottery.py --type qxc         # 抓取7星彩
    python scripts/fetch_lottery.py --type p5 --update # 增量更新排列5
    python scripts/fetch_lottery.py --type qxc --update # 增量更新7星彩
"""

import argparse
import sys

from lottery_common import (apply_patches, data_path, fetch_all_pages, fetch_incremental,
                            fetch_list_page, get_total_pages, load_existing, merge_data,
                            print_summary, save_data)

# 每种彩票对应的 Referer 和输出文件
LOTTERY_CONFIG = {
    "p3": {
        "name": "排列3",
        "item_type": "p3",
        "referer": "https://www.js-lottery.com/wfzq/p3p5/p3data",
        "output": "pl3_all_data.json",
        "digits": 3,
    },
    "p5": {
        "name": "排列5",
        "item_type": "p5",
        "referer": "https://www.js-lottery.com/wfzq/p3p5/p5data",
        "output": "pl5_all_data.json",
        "digits": 5,
    },
    "qxc": {
        "name": "7星彩",
        "item_type": "s7",
        "referer": "https://www.js-lottery.com/wfzq/sevenstar/data",
        "output": "qxc_all_data.json",
        "digits": 7,
    },
}


def main():
    parser = argparse.ArgumentParser(description="排列3/排列5 历史数据抓取")
    parser.add_argument("--type", required=True, choices=["p3", "p5", "qxc"], help="彩票类型")
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

    # 抓取数据
    if existing_data:
        # 增量：从最新页开始，追平已有数据即停止（通常 1-2 页）
        known = {item["issue_no"] for item in existing_data}
        print("  增量抓取（最新页起，追平后停止）...")
        all_data, caught_up = fetch_incremental(
            lambda page: fetch_list_page(config["item_type"], config["referer"], page), known)
        if not caught_up:
            print("  错误: 抓取失败或未追平，本次不更新数据")
            sys.exit(1)
    else:
        # 全量：探测总页数后并发抓取
        if args.pages:
            total_pages = args.pages
        else:
            print("  探测总页数...")
            total_pages = get_total_pages(config["item_type"], config["referer"])
        print(f"  总页数: {total_pages}")
        print(f"  开始抓取（{args.workers} 线程并发）...")
        all_data = fetch_all_pages(config["item_type"], config["referer"], total_pages, args.workers)

    # 合并去重
    all_data, added = merge_data(existing_data, all_data)
    if existing_data:
        print(f"  新增 {added} 条")

    # 应用数据修正（源数据的已知错误，见 scripts/data_patches.json）
    all_data = apply_patches(all_data, args.type)

    save_data(output_file, all_data)
    print_summary(all_data)


if __name__ == "__main__":
    main()
