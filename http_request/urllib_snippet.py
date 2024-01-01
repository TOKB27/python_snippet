### HTTPリクエスト等を行うurllibのスニペット ###

import urllib.request
import json

payload = {'key1': 'value1', 'key2': 'value2'}
payload = json.dumps(payload).encode('utf-8')

# GET
url = 'http://httpbin.org/get'
with urllib.request.urlopen(url) as f:
  print(f.read().decode('utf-8'))


# POST
req_post = urllib.request.Request('http://httpbin.org/post', data=payload, method='POST')
with urllib.request.urlopen(req_post) as f:
  print(json.loads(f.read().decode('utf-8')))


# PUT
req_put = urllib.request.Request('http://httpbin.org/put', data=payload, method='PUT')
with urllib.request.urlopen(req_put) as f:
  print(json.loads(f.read().decode('utf-8')))


# DELETE
req_delete = urllib.request.Request('http://httpbin.org/delete', data=payload, method='DELETE')
with urllib.request.urlopen(req_delete) as f:
  print(json.loads(f.read().decode('utf-8')))