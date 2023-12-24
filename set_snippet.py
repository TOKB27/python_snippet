### Pythonのset型（重複を許さない要素の集合）操作スニペット ###

# 要素の追加
set1 = {1, 2, 3}
set1.add(4)
print(set1) # {1, 2, 3, 4}


# 別のsetの追加
set1 = {1, 2, 3}
set2 = {3, 4, 5}
set1.update(set2)
print(set1) # {1, 2, 3, 4, 5}


# 要素の削除
## removeは削除対象が無いとエラー、discardは無くてもエラーにならない
set1 = {1, 2, 3}
set1.remove(2)
print(set1) # {1, 3}

set1 = {1, 2, 3}
set1.discard(2)
print(set1) # {1, 3}


# 要素を取り出して削除
set1 = {1, 2, 3}
pop_ele = set1.pop()
print(pop_ele) # 1
print(set1) # {2, 3}


# 全ての要素の削除
set1 = {1, 2, 3}
set1.clear()
print(set1) # set()


# 他のセットとの和集合を返す
set1 = {1, 2, 3}
set2 = {3, 4, 5}
union_set = set1.union(set2)
print(union_set) # {1, 2, 3, 4, 5}


# 他のセットとの積集合を返す
set1 = {1, 2, 3}
set2 = {3, 4, 5}
intersection_set = set1.intersection(set2)
print(intersection_set) # {3}


# 他のセットとの差集合を返す
## set1のみに存在する要素が取得可能
set1 = {1, 2, 3}
set2 = {3, 4, 5}
difference_set = set1.difference(set2)
print(difference_set) # {1, 2}


# 対象のセットが指定した別のセットの部分集合であるかどうか
set1 = {1, 2}
set2 = {1, 2, 3, 4}
result = set1.issubset(set2)
print(result) #True


# 対象のセットが指定した別のセットの上位集合であるかどうか
set1 = {1, 2, 3, 4}
set2 = {1, 2}
result = set1.issuperset(set2)
print(result) #True


# 対象のセットと指定した別のセットが共通の要素を持たないかどうか
set1 = {1, 2}
set2 = {3, 4}
result = set1.isdisjoint(set2)
print(result) #True