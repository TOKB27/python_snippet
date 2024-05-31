### HTTPリクエスト等を行うrequestsのスニペット ###

import requests

payload = {'key1': 'value1', 'key2': 'value2'}

# GET
r = requests.get('http://httpbin.org/get', params=payload, timeout=1)
# POST
r = requests.post('http://httpbin.org/post', data=payload, timeout=1)
# PUT
r = requests.put('http://httpbin.org/put', data=payload, timeout=1)
# DELETE
r = requests.delete('http://httpbin.org/delete', data=payload, timeout=1)

print(r.status_code)
print(r.text)
print(r.json())


# 例外処理
import requests

try:
    r = requests.get('http://httpbin.org/get', params=payload, timeout=1)
    r.raise_for_status()  # HTTPエラーが発生した場合、例外を投げる
except requests.exceptions.HTTPError as err:  # HTTPエラーが発生した場合の例外
    print(f"HTTP error occurred: {err}")
except Exception as err:  # 予期しない例外全て
    print(f"Other error occurred: {err}")
else:
    print('Success!')

