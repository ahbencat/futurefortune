import json

# 读取数据
with open(r'D:\Projects\lottory_pick\pl5_all_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 按期号前缀（年份）分组
from collections import defaultdict

year_groups = defaultdict(list)
for item in data:
    year_prefix = item['issue_no'][:2]
    year_groups[year_prefix].append(item)

print("各年份数据分布:")
print("-" * 40)
for year_prefix in sorted(year_groups.keys()):
    items = year_groups[year_prefix]
    issue_numbers = [int(item['issue_no']) for item in items]
    min_issue = min(issue_numbers)
    max_issue = max(issue_numbers)
    count = len(items)
    
    # 计算该年份应有的期号范围
    expected_count = max_issue - min_issue + 1
    missing = expected_count - count
    
    print(f"20{year_prefix}年: {count:4d}条, 期号范围: {min_issue:05d}-{max_issue:05d}, 缺失: {missing:4d}")

print("-" * 40)
print(f"总计: {len(data)}条")

# 检查是否有重复期号
issue_numbers = [item['issue_no'] for item in data]
unique_issues = set(issue_numbers)
print(f"\n唯一期号数: {len(unique_issues)}")
print(f"是否有重复: {'是' if len(unique_issues) != len(issue_numbers) else '否'}")

# 检查号码格式
invalid_format = 0
for item in data:
    if len(item['numbers']) != 5:
        invalid_format += 1
    else:
        for num in item['numbers']:
            if not num.isdigit() or int(num) < 0 or int(num) > 9:
                invalid_format += 1
                break

print(f"号码格式错误: {invalid_format}条")