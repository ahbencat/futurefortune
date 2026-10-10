import requests
import json
import re
import time

# 尝试不同的API接口
urls = [
    "https://m.china-lottery.cn/api/lottery/history?lotteryId=1004&pageNo=1&pageSize=1000",
    "https://m.china-lottery.cn/api/lottery/kjHistory?lotteryId=1004&pageNo=1&pageSize=1000",
    "https://m.china-lottery.cn/api/lottery/getKjHistory?lotteryId=1004&pageNo=1&pageSize=1000",
    "https://m.china-lottery.cn/api/lottery/queryKjHistory?lotteryId=1004&pageNo=1&pageSize=1000",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://m.china-lottery.cn/zschart?frm=z_baidu&lotteryId=1004&ct=T_BASE&md5=ae35310c5fafea74043fc6508e31362e&lotteryLength=1000'
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