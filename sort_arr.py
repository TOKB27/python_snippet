data = [
    {
        "id": 1,
        "difftype": "update",
        "info": {
            "score": 80
        }
    },
    {
        "id": 2,
        "difftype": "insert",
        "info": {
            "score": 60
        }
    },
    {
        "id": 3,
        "difftype": "delete",
        "info": {
            "score": 90
        }
    },
    {
        "id": 4,
        "difftype": "insert",
        "info": {
            "score": 85
        }
    }
]

# difftype の優先順位
difftype_order = {
    "insert": 0,
    "delete": 1,
    "update": 2,
}

sorted_data = sorted(
    data,
    key=lambda x: (
        difftype_order.get(x.get("difftype"), 99),
        x.get("info", {}).get("score", 0)
    )
)