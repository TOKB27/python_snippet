### グラフ描画ライブラリMatplotlib ###

import matplotlib.pyplot as plt

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
plt.bar(a, b)
# plt.barh(a, b) # 横棒の棒グラフ
plt.show()


