### グラフ描画ライブラリMatplotlib ###

import matplotlib.pyplot as plt
import numpy as np

x_data = [20, 40, 60, 80 ]
y_data = [10, 5, 3, 1]
plt.plot(x_data, y_data, marker="o")
# markerの指定は以下。
# “o” – 丸点
# “^” – 三角の点
# “s” – 四角の点

plt.savefig("graph.png")  # 保存
plt.show()  # 表示


## 棒グラフ ##
a = range(0, 5)
b = [4,8,3,6,9]
plt.bar(a, b)    # 縦棒の棒グラフ
# plt.barh(a, b) # 横棒の棒グラフ
plt.show()


## 散布図 ##
x = [14, 21, 42, 13, 25, 65]
y = [5, 15, 2, 25, 14, 35]
plt.scatter(x,y)
plt.show()


## 円グラフ ##
labels = ["A", "B", "C", "D", "E"]
data = [34, 22, 18, 43, 19]
ex = [0.1, 0, 0, 0, 0]
colors =["navy", "yellow", "blue", "red", "green"]
plt.pie(data, explode=ex, labels=labels, colors=colors, autopct="%1.1f%%", counterclock=False)
plt.show()
# autopct="%1.1f%%"は小数点の表示桁数。1.1とすると1つ。1.2とすると２つ
# explodeオプションで1つめの要素を10%ずらしている。
# counterclockオプションでFalseにすると時計回り、Trueだと反時計回り。


## ヒストグラム ##
x = np.random.normal(10, 10, 1000)  # 平均10、標準偏差10 の正規乱数を100件生成
plt.hist(x, bins=10)
# 引数にbins=数字でヒストグラムの棒の数を指定可能
# orientation="horizontal"を指定することで横棒として描画も可能
plt.show()
