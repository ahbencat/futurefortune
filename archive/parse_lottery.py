import re
import json

# 读取HTML文件
with open(r'D:\Projects\lottory_pick\lottery_all.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找所有期号数据
# 格式: issueName:"2026268",awArr:[d,a,a,h,g],...issueNo:26268
pattern = r'issueName:"(\d+)",awArr:\[([^\]]+)\],[^}]*issueNo:(\d+)'
matches = re.findall(pattern, content)

# 字母到数字的映射
letter_to_num = {
    'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4,
    'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9
}

# 解析数据
data = []
for match in matches:
    issue_name = match[0]
    aw_arr_str = match[1]
    issue_no = int(match[2])
    
    # 解析开奖号码
    letters = [l.strip() for l in aw_arr_str.split(',')]
    numbers = [letter_to_num.get(l, -1) for l in letters]
    
    data.append({
        'issue_no': issue_no,
        'issue_name': issue_name,
        'numbers': numbers
    })

# 按期号排序
data.sort(key=lambda x: x['issue_no'])

# 输出结果
print(f"总共找到 {len(data)} 期数据")
print(f"期号范围: {data[0]['issue_no']} - {data[-1]['issue_no']}")
print(f"\n前10期数据:")
for item in data[:10]:
    print(f"第{item['issue_no']}期: {item['numbers']}")

print(f"\n最后10期数据:")
for item in data[-10:]:
    print(f"第{item['issue_no']}期: {item['numbers']}")

# 保存为JSON文件
with open(r'D:\Projects\lottory_pick\lottery_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n数据已保存到 lottery_data.json")