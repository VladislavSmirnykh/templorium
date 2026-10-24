"""Parse the ``cids`` browser cookie (comma-separated UUIDs or legacy dash-separated ints)."""


def parse_company_cookie(value: str) -> list:
    if not value:
        return []
    if "," in value:
        return [part for part in value.split(",") if part]
    if len(value) == 36 and value.count("-") == 4:
        return [value]
    parts = value.split("-")
    if parts and all(part.isdigit() for part in parts):
        return [int(part) for part in parts]
    return []
