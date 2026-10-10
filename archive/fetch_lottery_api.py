import requests
import json
import time

# 中国体育彩票官方API
# 排列5的 lotteryId 是 1004
base_url = "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.lottery.gov.cn/',
    'Origin': 'https://www.lottery.gov.cn'
}

# 尝试获取数据
params = {
    'lotteryId': '1004',
    'pageNo': '1',
    'pageSize': '1000'
}

try:
    print(f"尝试API: {base_url}")
    response = requests.get(base_url, params=params, headers=headers, timeout=15)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"响应数据: {json.dumps(data, ensure_ascii=False)[:1000]}")
        
        # 保存完整响应
        with open(r'D:\Projects\lottory_pick\lottery_api_response.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("\n完整响应已保存到 lottery_api_response.json")
    else:
        print(f"响应内容: {response.text[:500]}")
except Exception as e:
    print(f"错误: {e}")