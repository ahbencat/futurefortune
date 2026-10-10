#!/usr/bin/env python3
"""
排列三数据派生脚本：排列三 = 排列五前三位号码，无需单独爬取。

用法:
    python scripts/derive_p3.py

说明:
    只对 pl3_all_data.json 中**尚不存在**的期号做派生，已有一律保留。
    原因：排列三与排列五早期（04009-04020）是独立摇奖，前三位并不相同，
    直接整体重算会覆盖这 12 条正确记录。
"""

import sys

from lottery_common import (apply_patches, data_path, load_existing, merge_data,
                            print_summary, save_data)

P5_FILE = "pl5_all_data.json"
P3_FILE = "pl3_all_data.json"


def p3_from_p5(item: dict) -> dict:
    """排列五记录 -> 排列三记录（取前三位）"""
    return {
        "date": item["date"],
        "issue_no": item["issue_no"],
        "numbers": item["numbers"][:3],
    }


def main():
    p5_path = data_path(P5_FILE)
    p3_path = data_path(P3_FILE)

    print("=== 排列三 数据派生（取自排列五前三位）===")
    print(f"来源: {p5_path}")
    print(f"输出: {p3_path}")

    p5_data = load_existing(p5_path)
    if not p5_data:
        print(f"未找到排列五数据 {p5_path}，退出")
        sys.exit(1)

    existing = load_existing(p3_path)
    if not existing:
        print("警告: 未找到已有排列三数据，将全部派生——")
        print("      注意 04009-04020 期间两个玩法是独立摇奖，派生结果与原数据不符")
    else:
        print(f"已有数据: {len(existing)} 条")

    known = {item["issue_no"] for item in existing}
    derived = [p3_from_p5(item) for item in p5_data if item["issue_no"] not in known]

    merged, added = merge_data(existing, derived)
    print(f"  新增 {added} 条（排列五共 {len(p5_data)} 条）")

    # 应用数据修正（排列三 04001-04008 早于排列五上市，需从官方数据补入）
    merged = apply_patches(merged, "pl3")

    save_data(p3_path, merged)
    print_summary(merged)


if __name__ == "__main__":
    main()
