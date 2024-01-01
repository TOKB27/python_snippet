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
