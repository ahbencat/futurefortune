import json
from datetime import datetime, timedelta

# 读取数据
with open(r'D:\Projects\lottory_pick\pl5_all_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 获取最近几期的日期
recent_dates = []
for item in data[-20:]:
    date = datetime.strptime(item['date'], '%Y-%m-%d')
    recent_dates.append((item['issue_no'], date))

print("最近20期开奖日期:")
print("-" * 50)
for issue_no, date in recent_dates:
    weekday = date.strftime('%A')
    print(f"{issue_no}: {date.strftime('%Y-%m-%d')} ({weekday})")

# 分析开奖规律
print("\n开奖规律分析:")
print("-" * 50)

# 检查是否每天开奖
date_diffs = []
for i in range(1, len(recent_dates)):
    diff = (recent_dates[i][1] - recent_dates[i-1][1]).days
    date_diffs.append(diff)

print(f"最近期间间隔天数: {date_diffs}")

# 检查周末是否开奖
weekend_draws = []
for issue_no, date in recent_dates:
    if date.weekday() >= 5:  # 5=Saturday, 6=Sunday
        weekend_draws.append((issue_no, date))

print(f"\n周末开奖次数: {len(weekend_draws)}")
if weekend_draws:
    for issue_no, date in weekend_draws:
        print(f"  {issue_no}: {date.strftime('%Y-%m-%d')} ({date.strftime('%A')})")

# 预测下一期
last_date = recent_dates[-1][1]
last_issue = int(recent_dates[-1][0])

print(f"\n最新一期: {last_issue}期, {last_date.strftime('%Y-%m-%d')} ({last_date.strftime('%A')})")

# 根据规律预测下一期
# 如果每天开奖，下一期是明天
# 如果周末不开奖，需要找到下一个工作日

next_date = last_date + timedelta(days=1)
while next_date.weekday() >= 5:  # 跳过周末
    next_date += timedelta(days=1)

next_issue = last_issue + 1

print(f"\n预测下一期:")
print(f"  期号: {next_issue:05d}")
print(f"  日期: {next_date.strftime('%Y-%m-%d')} ({next_date.strftime('%A')})")

# 检查是否有节假日影响
print(f"\n注意: 以上预测基于历史开奖规律，实际开奖时间可能因节假日调整。")