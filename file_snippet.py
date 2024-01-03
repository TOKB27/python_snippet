### ファイル操作スニペット ###

# ファイルの書き込み
f = open('file.txt', 'w')
f.write('ファイルの書き込み\n')
f.close()

# withステートメントでopen
with open('file.txt', 'w') as f:
  f.write('ABCDEFG')
f.close()

# ファイルへの追記
with open('file.txt', 'a') as f:
  f.write('HIJKLMN')
f.close()

# ファイルの読み込み
with open('file.txt', 'r') as f:
  print(f.read())
f.close()

# 一行ずつ読み込んで処理する
with open('file.txt', 'r') as f:
  while True:
    line = f.readline()
    print(line)
    if not line:
      break
f.close()


# 2文字ずつ読み込んで処理する
with open('file.txt', 'r') as f:
  while True:
    chunk = 2
    line = f.read(chunk)
    print(line)
    if not line:
      break
f.close()