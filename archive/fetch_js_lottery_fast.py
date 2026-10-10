import requests
import json
import re
import time

# 江苏体彩网排列5历史数据API
base_url = "https://www.js-lottery.com/Lottery/_ListData"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.js-lottery.com/wfzq/p3p5/p5data',
    'X-Requested-With': 'XMLHttpRequest'
}

# 尝试使用更大的pageSize
all_data = []
page = 1
max_pages = 100  # 先获取前100页看看

print(f"开始获取排列5历史数据...")

while page <= max_pages:
    try:
        params = {
            'itemType': 'p5',
            'pageindex': str(page),
            'size': '100'  # 尝试每页100条
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            html = response.text
            
            # 解析HTML中的数据
            pattern = r'<td style="text-align:center;">(\d{4}-\d{2}-\d{2})</td>\s*<td style="text-align:center;">(\d+)</td>\s*<td style="text-align:center;">\s*([\d\s]+)\s*</td>'
            matches = re.findall(pattern, html)
            
            if matches:
                for match in matches:
                    date = match[0]
                    issue_no = match[1]
                    numbers_str = match[2].strip()
                    numbers = numbers_str.split()
                    
                    all_data.append({
                        'date': date,
                        'issue_no': issue_no,
                        'numbers': numbers
                    })
                
                print(f"第 {page} 页: 获取 {len(matches)} 条数据，累计 {len(all_data)} 条")
            else:
                print(f"第 {page} 页没有数据，停止获取")
                break
        else:
            print(f"第 {page} 页请求失败，状态码: {response.status_code}")
            break
            
        page += 1
        time.sleep(0.3)  # 减少间隔时间
        
    except Exception as e:
        print(f"第 {page} 页错误: {e}")
        break

# 保存数据
print(f"\n总共获取 {len(all_data)} 条数据")

if all_data:
    # 按期号排序
    all_data.sort(key=lambda x: int(x['issue_no']))
    
    print(f"期号范围: {all_data[0]['issue_no']} - {all_data[-1]['issue_no']}")
    
    # 保存为JSON
    with open(r'D:\Projects\lottory_pick\pl5_all_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print("数据已保存到 pl5_all_data.json")
    
    # 显示前10条和后10条
    print("\n前10条数据:")
    for item in all_data[:10]:
        print(f"期号: {item['issue_no']}, 号码: {item['numbers']}, 日期: {item['date']}")
    
    print("\n后10条数据:")
    for item in all_data[-10:]:
        print(f"期号: {item['issue_no']}, 号码: {item['numbers']}, 日期: {item['date']}")