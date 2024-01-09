### ファイル操作スニペット ###

import os
import pathlib
import glob
import shutil


# ファイル作成
print('file_test.txt作成します。')
pathlib.Path('file_test.txt').touch()
if os.path.exists('file_test.txt'):
  print('exist file_test.txt')
else:
  print('not exist file_test.txt')

# ファイル削除
print('file_test.txt削除します。')
os.remove('file_test.txt')
if os.path.exists('file_test.txt'):
  print('exist file_test.txt')
else:
  print('not exist file_test.txt')

# ディレクトリ作成
print('test.dir作成します。')
os.mkdir('test_dir')
if os.path.exists('test_dir'):
  print('exist test.dir')
else:
  print('not exist test_dir')
  
# ディレクトリ削除
print('test.dir削除します。')
os.rmdir('test_dir')
if os.path.exists('test_dir'):
  print('exist test.dir')
else:
  print('not exist test_dir')

# リネーム
print('リネームでrename.txtを作成します')
pathlib.Path('file_test.txt').touch()
os.rename('file_test.txt', 'rename.txt')
if os.path.exists('rename.txt'):
  print('exist rename.txt')
os.remove('rename.txt')

# シンボリックリンク
print('シンボリックリンクでsymlink.txtを作成します')
pathlib.Path('file_test.txt').touch()
os.symlink('file_test.txt', 'symlink.txt')
if os.path.exists('symlink.txt'):
  print('exist symlink.txt')
os.unlink('symlink.txt')

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
