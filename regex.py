import re


# 最初に一致した部分を検索(search)
pattern = re.compile(r'[246]')
text = '12345678'
match = pattern.search(text)
if match:
  print('Match found:', match.group()) # Match found: 2
else:
  print('Match not found')


# 一致する全ての箇所を検索(findall)
pattern = re.compile(r'[246]')
text = '12345678'
match = pattern.findall(text)
print(match) # ['2', '4', '6']


# 一致箇所の置換(sub)
pattern = re.compile(r'[246]')
text = '12345678'
updated_text = pattern.sub('X', text)
print(updated_text)  # 1X3X5X78


### 正規表現作成例 ###

# 直前の文字を1回以上繰り返し(+)
pattern = re.compile(r'gre+n')
text = "green"
match = pattern.search(text)
if match:
  print('Match found:', match.group()) # Match found: green
else:
  print('Match not found')


# 直前の文字を0回以上繰り返し(*)
pattern = re.compile(r'gre*n')
text = "green"
match = pattern.search(text)
if match:
  print('Match found:', match.group()) # Match found: green
else:
  print('Match not found')


# 直前の文字が0か1個(?)
pattern = re.compile(r'gre?n')
text = "gren" # greenだとマッチしない
match = pattern.search(text)
if match:
  print('Match found:', match.group()) # Match found: gren
else:
  print('Match not found')


# 直前の文字が1回以上繰り返し(+?)
pattern = re.compile(r'gre+?n')
text = "green"
match = pattern.search(text)
if match:
  print('Match found:', match.group()) # Match found: green
else:
  print('Match not found')


# 直前の文字が0回以上繰り返し(*?)
pattern = re.compile(r'gre*?n')
text = "grn"
match = pattern.search(text)
if match:
  print('Match found:', match.group()) # Match found: grn
else:
  print('Match not found')

pattern = re.compile(r'0[789]0-[0-9]{4}-\d{4}')

# 携帯電話の正規表現
pattern = re.compile(r'0[789]0-[0-9]{4}-\d{4}')

# [0-9]{4}は0から9までの数字が4回繰り返されることを示す
# \dは任意の数字を示す
# 任意の一文字は.