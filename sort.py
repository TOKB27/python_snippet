# 辞書 → 辞書 の場合
data = {
    "a": {"score": 80, "age": 25},
    "b": {"score": 60, "age": 30},
    "c": {"score": 90, "age": 22},
}

sorted_data = dict(
    sorted(data.items(), key=lambda x: x[1]["score"])
)

# 複数キーでソート
sorted_data = sorted(
    data.items(),
    key=lambda x: (x[1]["age"], x[1]["score"])
)

# 辞書 → リスト → 辞書 の場合
data = {
    "users": [
        {"name": "tanaka", "age": 30},
        {"name": "sato", "age": 25},
        {"name": "suzuki", "age": 40},
    ]
}

data["users"] = sorted(
    data["users"],
    key=lambda x: x["age"]
)
