import json

# 读取数据
with open(r'D:\Projects\lottory_pick\pl5_all_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"总记录数: {len(data)}")

# 检查期号范围
issue_numbers = [int(item['issue_no']) for item in data]
min_issue = min(issue_numbers)
max_issue = max(issue_numbers)

print(f"最小期号: {min_issue:05d}")
print(f"最大期号: {max_issue:05d}")

# 检查是否有重复期号
unique_issues = set(issue_numbers)
print(f"唯一期号数: {len(unique_issues)}")
print(f"是否有重复: {'是' if len(unique_issues) != len(issue_numbers) else '否'}")

# 检查是否有缺失的期号
all_issues = set(range(min_issue, max_issue + 1))
missing = sorted(all_issues - unique_issues)
print(f"理论期号数: {len(all_issues)}")
print(f"缺失期号数: {len(missing)}")

if missing and len(missing) <= 20:
    print(f"缺失的期号: {missing}")
elif missing:
    print(f"前20个缺失的期号: {missing[:20]}")

# 检查最后几期
print(f"\n最后5条数据:")
for item in data[-5:]:
    print(f"  {item['issue_no']}: {item['numbers']} ({item['date']})")

# 检查是否有空数据
empty_count = sum(1 for item in data if len(item['numbers']) != 5)
print(f"\n号码不为5位的记录数: {empty_count}")