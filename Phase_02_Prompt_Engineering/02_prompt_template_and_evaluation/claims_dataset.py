
claims_dataset = [
    {
        "id": 1,
        "claim": (
            "A pipe burst in my house, but I have no repair estimate."
        ),
        "expected_category": "Property Damage",
        "required_missing": [
            "repair estimate",
            "damage extent",
        ],
    },
    {
        "id": 2,
        "claim": (
            "My car was hit in a parking lot, and the other driver left."
        ),
        "expected_category": "Vehicle Damage",
        "required_missing": [
            "incident date",
            "damage details",
        ],
    },
    {
        "id": 3,
        "claim": (
            "My laptop was stolen from my office, but I have no police report."
        ),
        "expected_category": "Theft",
        "required_missing": [
            "police report",
            "theft date",
        ],
    },
    {
        "id": 4,
        "claim": (
            "I paid for an emergency hospital visit after an accident."
        ),
        "expected_category": "Medical Expense",
        "required_missing": [
            "medical bill",
            "accident details",
        ],
    },
    {
        "id": 5,
        "claim": (
            "A storm damaged the roof of my house yesterday."
        ),
        "expected_category": "Property Damage",
        "required_missing": [
            "damage estimate",
            "damage extent",
        ],
    },
]

