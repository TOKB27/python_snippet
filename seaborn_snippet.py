### matplotlibを基盤として構築されたデータ可視化ライブラリ ###
### matplotlibと比べて少ないコードで洗練された図を描くことができる ###

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


## 棒グラフの作成 ##
data = {
    'Category': ['A', 'B', 'C', 'D', 'E'],
    'Values': [23, 17, 35, 29, 12]
}
df = pd.DataFrame(data)

# 棒グラフの作成
sns.barplot(x='Category', y='Values', data=df)

# プロットの表示
plt.show()


## ヒストグラムの作成 ##
# 正規分布に従うランダムデータを生成
np.random.seed(1)  # シード値を設定すると、そのアルゴリズムが同じシード値に対して常に同じ一連の乱数を生成
data = np.random.randn(1000)  #1000個の乱数を生成

# ヒストグラムの作成
sns.histplot(data, bins=30, kde=True)
# bins=30でヒストグラムのビンの数を設定
# kde=Trueはカーネル密度推定、データの分布を滑らかに可視化

# プロットの表示
plt.show()