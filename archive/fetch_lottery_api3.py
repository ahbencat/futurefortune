import requests
import json
import time

# 中国体育彩票官方API
base_url = "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.lottery.gov.cn/',
    'Origin': 'https://www.lottery.gov.cn'
}

# 尝试不同的参数组合
param_sets = [
    {
        'lottoId': '1004',
        'pageNo': '1',
        'pageSize': '100'
    },
    {
        'lotteryId': '1004',
        'page': '1',
        'size': '100'
    },
    {
        'lotteryId': '1004',
        'pageNum': '1',
        'pageSize': '100'
    },
    {
        'lotteryId': '1004',
        'pageNo': '1',
        'pageSize': '100',
        'type': '0'
    },
    {
        'lotteryId': '1004',
        'pageNo': '1',
        'pageSize': '100',
        'platform': '0'
    }
]

for params in param_sets:
    try:
        print(f"尝试参数: {params}")
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False)[:500]}")
            
            if data.get('success'):
                print("成功获取数据！")
                # 保存完整响应
                with open(r'D:\Projects\lottory_pick\lottery_api_response.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("完整响应已保存")
                break
        print("---")
        time.sleep(1)
    except Exception as e:
        print(f"错误: {e}")
        print("---")