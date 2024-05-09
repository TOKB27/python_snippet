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

# 平均
print(df.mean())
# 列1    2.0
# dtype: float64

## 並べ替え ##
data = {'列1': [2, 4, 3, 1, 0],
        '列2': [9, 5, 8, 6, 7]}
df = pd.DataFrame(data)
print(df)
#    列1  列2
# 0   2   9
# 1   4   5
# 2   3   8
# 3   1   6
# 4   0   7

# 列1を昇順に並べ替え
df_as = df.sort_values(by='列1')
print(df_as)
#    列1  列2
# 4   0   7
# 3   1   6
# 0   2   9
# 2   3   8
# 1   4   5

# 列1を降順に並べ替え
df_de = df.sort_values(by='列1', ascending=False)
print(df_de)
#    列1  列2
# 1   4   5
# 2   3   8
# 0   2   9
# 3   1   6
# 4   0   7


## データの選択 ##

# df.iloc[行, 列]
print(df.iloc[0, 0])
# 2
print(df.iloc[1, 1])
# 5

# すべての行の、最後の列を選択
t = df.iloc[:, -1]
print(t)
# 0    9
# 1    5
# 2    8
# 3    6
# 4    7
# Name: 列2, dtype: int64

# 列2が7より大きい要素を選択
mask = df['列2'] > 7
print(mask)
# 0     True
# 1    False
# 2     True
# 3    False
# 4    False
# Name: 列2, dtype: bool

print(df[mask])
#    列1  列2
# 0   2   9
# 2   3   8

# 1行にまとめて書く場合
print(df[df['列2'] > 7])
#    列1  列2
# 0   2   9
# 2   3   8

# 複数の条件指定
print(df[(df['列2'] > 7) & (df['列1'] > 2)])
#    列1  列2
# 2   3   8


## 置換 ##

# 新しい列 target を None で初期化
df['target'] = None
print(df)
#    列1  列2 target
# 0   2   9   None
# 1   4   5   None
# 2   3   8   None
# 3   1   6   None
# 4   0   7   None

# 2より大きい時は「over」、2以下は「under」に置換する。
mask1 = df['列1'] > 2
mask2 = df['列1'] <= 2
df.loc[mask1, 'target'] = 'over'
df.loc[mask2, 'target'] = 'under'
print(df)
#    列1  列2 target
# 0   2   9  under
# 1   4   5   over
# 2   3   8   over
# 3   1   6  under
# 4   0   7  under


# 欠損値のあるレコードを削除
df.iloc[0, 0] = None
print(df)
#     列1  列2 target
# 0  NaN   9  under
# 1  4.0   5   over
# 2  3.0   8   over
# 3  1.0   6  under
# 4  0.0   7  under
df_dropna = df.dropna()
print(df_dropna)
#     列1  列2 target
# 1  4.0   5   over
# 2  3.0   8   over
# 3  1.0   6  under
# 4  0.0   7  under


## NumPyのndarrayとの変換 ##

# ndarrayへの変換
print(type(df_dropna))
# <class 'pandas.core.frame.DataFrame'>
print(type(df_dropna.values))
# <class 'numpy.ndarray'>
print(df_dropna.values)
# [[4.0 5 'over']
#  [3.0 8 'over']
#  [1.0 6 'under']
#  [0.0 7 'under']]

# ndarrayからpd.DataFrameへの変換
import numpy as np
df = pd.DataFrame(
    data=np.random.randn(5, 5)
)
print(df)
#           0         1         2         3         4
# 0  0.223668  0.014736  0.532476 -0.814704 -0.344570
# 1  0.422887  0.522609 -0.552856 -0.522329  0.578230
# 2  1.248147  0.371750  1.011887  0.346325  0.918026
# 3 -0.242473  0.771075 -0.586427  0.080307  1.132582
# 4 -0.069031 -0.065962  1.595269 -0.967261  1.079485