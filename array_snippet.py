### Pythonの配列操作スニペット ###

# 要素のアクセス
list1 = [1, 2, 3, 4, 5]
print(list1[0])  # 1

# スライシング
list1 = [1, 2, 3, 4, 5]
slice = list1[1:4]
print(slice) # [2, 3, 4]

# 要素の変更
list1 = [1, 2, 3, 4, 5]
list1[2] = 10
print(list1)  # [1, 2, 10, 4, 5]

# 要素の追加
list1 = [1, 2, 3, 4, 5]
list1.append(6)
print(list1)  # [1, 2, 3, 4, 5, 6]

# 要素の削除
list1 = [1, 2, 3, 4, 5]
list1.remove(3)
print(list1)  # [1, 2, 4, 5]

del list1[1]
print(list1)  # [1, 4, 5]


# 要素を取り出して削除
list1 = [10, 20, 30]
pop_ele = list1.pop(1)
print(pop_ele) # 20
print(list1) # [10, 30]

# リストの結合
list1 = [1, 2, 3]
list2 = [4, 5, 6]
result = list1 + list2
print(result)  # [1, 2, 3, 4, 5, 6]


# リストの拡張
list1 = [1, 2, 3]
list2 = [4, 5, 6]
list1.extend(list2)
print(list1)  # [1, 2, 3, 4, 5, 6]


# 特定要素のカウント
list1 = [1, 2, 3, 3]
print(list1.count(3)) # 2


# クリア
list1 = [1, 2, 3]
list1.clear()
print(list1) # []


## ソート ##

# 順番反転
list1 = [1, 2, 3]
list1.reverse()
print(list1) # [3, 2, 1]


# ソート
list1 = [2, 4, 3, 1]
list1.sort()
print(list1) # [1, 2, 3, 4]


# アルファベット順ソート
list1 = ["apple", "melon", "banana"]
list1.sort()
print(list1) # ['apple', 'banana', 'melon']


# 降順ソート
list1 = [2, 4, 3, 1]
list1.sort(reverse=True)
print(list1) # [4, 3, 2, 1]


## リスト内包表記 ##

# 基本的なリスト内包表記
squares = [x**2 for x in range(10)]
print(squares)
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# 条件付きリスト内包表記
evens = [x for x in range(10) if x % 2 == 0]
print(evens)
# [0, 2, 4, 6, 8]

# ネストしたリスト内包表記
combinations = [(x, y) for x in range(3) for y in range(3)]
print(combinations)
# [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]