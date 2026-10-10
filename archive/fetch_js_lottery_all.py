import requests
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 江苏体彩网排列5历史数据API
base_url = "https://www.js-lottery.com/Lottery/_ListData"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.js-lottery.com/wfzq/p3p5/p5data',
    'X-Requested-With': 'XMLHttpRequest'
}

def fetch_page(page):
    """获取单页数据"""
    try:
        params = {
            'itemType': 'p5',
            'pageindex': str(page),
            'size': '10'
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            html = response.text
            
            # 解析HTML中的数据
            pattern = r'<td style="text-align:center;">(\d{4}-\d{2}-\d{2})</td>\s*<td style="text-align:center;">(\d+)</td>\s*<td style="text-align:center;">\s*([\d\s]+)\s*</td>'
            matches = re.findall(pattern, html)
            
            page_data = []
            for match in matches:
                date = match[0]
                issue_no = match[1]
                numbers_str = match[2].strip()
                numbers = numbers_str.split()
                
                page_data.append({
                    'date': date,
                    'issue_no': issue_no,
                    'numbers': numbers
                })
            
            return page_data
        else:
            return []
    except Exception as e:
        return []

# 总页数
total_pages = 774  # 7735 / 10 = 774 页

print(f"开始获取排列5历史数据，共 {total_pages} 页...")

all_data = []

# 使用线程池并发获取数据
with ThreadPoolExecutor(max_workers=10) as executor:
    # 提交所有任务
    future_to_page = {executor.submit(fetch_page, page): page for page in range(1, total_pages + 1)}
    
    # 处理完成的任务
    completed = 0
    for future in as_completed(future_to_page):
        page = future_to_page[future]
        try:
            page_data = future.result()
            all_data.extend(page_data)
            completed += 1
            
            if completed % 50 == 0:
                print(f"已完成 {completed}/{total_pages} 页，累计 {len(all_data)} 条数据")
        except Exception as e:
            print(f"第 {page} 页错误: {e}")

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