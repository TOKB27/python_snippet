### データ加工に使われるpandasのSeriesスニペット ###
### Seriesは1次元のデータ ###

import pandas as pd

# リストからSeriesを作成
data = [1, 2, 3, 4, 5]
series_from_list = pd.Series(data)

# 辞書からSeriesを作成
data_dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
series_from_dict = pd.Series(data_dict)


# 値にアクセス
print(series_from_list[2])  # インデックス2の値を取得
# 3


# スライシング
print(series_from_list[1:4])  # インデックス1から3の範囲を取得
# 1    2
# 2    3
# 3    4
# dtype: int64


# 条件に合致する要素を選択
print(series_from_list[series_from_list > 2])
# 2    3
# 3    4
# 4    5
# dtype: int64

# インデックスを指定してSeriesを作成
custom_index = ['one', 'two', 'three', 'four', 'five']
series_with_custom_index = pd.Series(data, index=custom_index)

print(series_with_custom_index)
# one      1
# two      2
# three    3
# four     4
# five     5
# dtype: int64

# インデックスと値の取得
print(series_with_custom_index.index) # Index(['one', 'two', 'three', 'four', 'five'], dtype='object')
print(series_with_custom_index.values) # [1 2 3 4 5]


# Seriesの長さを取得
print(len(series_with_custom_index)) # 5


# スカラー演算
result = series_from_list * 2
print(result)
# 0     2
# 1     4
# 2     6
# 3     8
# 4    10
# dtype: int64


# 要素ごとの演算
result = series_from_list + series_from_list
print(result)
# 0     2
# 1     4
# 2     6
# 3     8
# 4    10
# dtype: int64