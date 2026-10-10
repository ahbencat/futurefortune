import requests
import json
import re
import time

# 尝试第三方彩票数据API
urls = [
    "https://api.jisuapi.com/lottery/history?appkey=test&lottery_id=1004&page=1&page_size=1000",
    "https://www.lottery.gov.cn/api/lottery_kj_history_new.jspx?lotteryId=1004&pageNo=1&pageSize=1000",
    "https://m.china-lottery.cn/api/lottery/history?lotteryId=1004&pageNo=1&pageSize=1000",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

for url in urls:
    try:
        print(f"尝试: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应内容: {response.text[:500]}")
            print("---")
        time.sleep(1)
    except Exception as e:
        print(f"错误: {e}")
        print("---")

# 尝试直接解析HTML页面
print("\n尝试解析HTML页面...")
try:
    with open(r'D:\Projects\lottory_pick\lottery_page.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有期号数据
    pattern = r'issueName:"(\d+)",awArr:\[([^\]]+)\],[^}]*issueNo:(\d+)'
    matches = re.findall(pattern, content)
    print(f"找到 {len(matches)} 条数据")
    
    if matches:
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
    else:
        print("未找到数据")
except Exception as e:
    print(f"错误: {e}")