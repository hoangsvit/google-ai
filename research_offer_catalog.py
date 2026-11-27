"""Unverified offer references from the upstream Android research guide.

These are display labels only, not product IDs, eligibility assertions or
executable billing instructions.
"""

OFFER_REFERENCES = (
    ("Google AI Pro 5TB", "12 months free"),
    ("Google AI Pro 5TB", "6-month extension (unverified)"),
    ("Google AI Pro 5TB", "3 months free"),
    ("Google AI Pro 5TB", "USD 1.99/month for 12 months"),
    ("Google AI Pro 5TB", "USD 1.99/month for 3 months"),
    ("Google AI Pro 5TB", "USD 0.99 for 1 month"),
    ("Google AI Plus 400GB", "USD 0.49/month for 12 months"),
    ("Google AI Plus 2TB", "USD 0.99/month for 3 months"),
    ("Google AI Plus 2TB", "USD 1.49/month for 3 months"),
    ("Google AI Ultra 20TB", "USD 9.99/month for 3 months"),
    ("Google AI Ultra 20TB", "USD 19.99/month for 3 months"),
    ("Google AI Ultra 30TB", "USD 19.99/month for 3 months"),
    ("Google AI Ultra 30TB", "USD 49.99/month for 3 months"),
    ("Google One 100GB", "1 month free"),
    ("Google One 2TB", "1 month free"),
    ("YouTube Premium", "1 month free; reported Google One prerequisite"),
)


def reference_options():
    return [(f"{name} — {terms}", index)
            for index, (name, terms) in enumerate(OFFER_REFERENCES)]
