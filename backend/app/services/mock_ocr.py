import random
from datetime import date, timedelta
from typing import Any


FIELDS = (
    "fdr_number",
    "bank_id",
    "depositor_name",
    "principal_amount",
    "currency",
    "issue_date",
    "maturity_date",
    "beneficiary_name",
    "lien_status",
    "lien_in_favour_of",
)

BANKS = tuple(f"DEMO-BANK-{index:02d}" for index in range(1, 7))
DEPOSITORS = (
    "Aarav Sharma",
    "Ananya Iyer",
    "Rohan Deshmukh",
    "Priya Patel",
    "Vikram Sengupta",
    "Kavya Nair",
    "Aditya Agarwal",
    "Meera Mehta",
)


def generate_mock_extraction(seed: str) -> tuple[list[dict[str, Any]], str]:
    """Create persisted synthetic extraction values; this function never reads the document."""
    rng = random.Random(seed)
    issue_date = date(2025, 1, 1) + timedelta(days=rng.randint(0, 900))
    maturity_date = issue_date + timedelta(days=rng.choice((365, 540, 730, 1095)))
    values = {
        "fdr_number": f"FDR-2026-{rng.randint(100000, 999999)}",
        "bank_id": rng.choice(BANKS),
        "depositor_name": rng.choice(DEPOSITORS),
        "principal_amount": f"{rng.randrange(100_000, 5_000_001, 10_000):.2f}",
        "currency": "INR",
        "issue_date": issue_date.isoformat(),
        "maturity_date": maturity_date.isoformat(),
        "beneficiary_name": "AICTE (synthetic demo)",
        "lien_status": rng.choice(("MARKED", "MARKED", "PENDING REVIEW")),
        "lien_in_favour_of": "AICTE (synthetic demo)",
    }

    fields = []
    for index, field in enumerate(FIELDS):
        x = 35 + (index % 2) * 410
        y = 55 + (index // 2) * 80
        value = values[field]
        fields.append({
            "field": field,
            "raw_value": value,
            "normalized_value": value,
            "confidence": round(rng.uniform(0.86, 0.99), 4),
            "page": 1,
            "bounding_box": [[x, y], [x + 260, y], [x + 260, y + 32], [x, y + 32]],
            "review_status": "MOCK_GENERATED",
        })

    raw_text = (
        "MOCK EXTRACTION SIMULATION — GENERATED VALUES ONLY — "
        "NO DOCUMENT OCR WAS PERFORMED."
    )
    return fields, raw_text
