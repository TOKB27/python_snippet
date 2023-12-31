### データ加工に使われるpandasのSeriesスニペット ###
### DataFlameは2次元のデータ ###

import pandas as pd


# リストからの作成
data = {'列1': [1, 2, 3],
        '列2': ['A', 'B', 'C']}
df = pd.DataFrame(data)

# CSVファイルからの読み込み
# df = pd.read_csv('ファイル名.csv')

# 先頭3行までの出力
print("先頭3行までの出力")
print(df.head(3))
#    列1 列2
# 0   1  A
# 1   2  B
# 2   3  C


# 列のデータ型の出力
print("列のデータ型の出力")
print(df.dtypes)
# 列1     int64
# 列2    object
# dtype: object


# 列の選択
column1 = df['列1']
print("列の選択")
print(column1)
# 0    1
# 1    2
# 2    3
# Name: 列1, dtype: int64


# 複数の列の選択
subset = df[['列1', '列2']]
print("複数の列の選択")
print(subset)
#    列1 列2
# 0   1  A
# 1   2  B
# 2   3  C


# 行の選択
row = df.loc[0]  # インデックスを指定して選択
print("行の選択")
print(row)
# 列1    1
# 列2    A
# Name: 0, dtype: object


# データのフィルタリング
filtered_data = df[df['列1'] > 2]
print("データのフィルタリング")
print(filtered_data)
#    列1 列2
# 2   3  C


# データのソート
sorted_df = df.sort_values(by='列1', ascending=False)
print("データのソート")
print(sorted_df)
#    列1 列2
# 2   3  C
# 1   2  B
# 0   1  A


# データのグループ化
grouped_data = df.groupby('列2').mean()
print("データのグループ化")
print(grouped_data)
# 列2    
# A    1
# B    2
# C    3


# 列の追加
df['追加列'] = [4, 5, 6]
print("列の追加")
print(df)
#    列1 列2  追加列
# 0   1  A    4
# 1   2  B    5
# 2   3  C    6


# 列の削除
# axis=0は行方向（行を基準とした操作）、axis=1は列方向（列を基準とした操作）を指す
df = df.drop('追加列', axis=1)
print("列の削除")
print(df)
#    列1 列2
# 0   1  A
# 1   2  B
# 2   3  C

# 行の削除
df = df.drop(1, axis=0)
print("行の削除")
print(df)
#    列1 列2
# 0   1  A
# 2   3  C