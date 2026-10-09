"""Investor-facing sectors and industry groups, mapped from SEC SIC codes.

GICS-like sector names are used as plain English labels; this is NOT the GICS
classification (which is licensed), it is a documented mapping from the SIC code
each company reports to the SEC. Rules are ordered: the first rule whose SIC range
contains the company's code wins, so specific ranges come before broad ones. A short
ticker override list fixes large, well-known misfits (each with a reason). Published
as docs/sectors.html; bump MAPPING_VERSION whenever a rule changes.
"""

from __future__ import annotations

MAPPING_VERSION = "2026-10-09.1"

SECTORS = [
    "Communication Services", "Consumer Discretionary", "Consumer Staples", "Energy", "Financials",
    "Health Care", "Industrials", "Information Technology", "Materials", "Real Estate", "Utilities",
]

CS, CD, ST, EN, FI, HC, IN, IT, MA, RE, UT = SECTORS

# industry group -> sector
GROUPS: dict[str, str] = {
    "Software": IT, "IT Services": IT, "Semiconductors": IT, "Tech Hardware": IT,
    "Communications Equipment": IT, "Electronic Components & Instruments": IT,
    "Interactive Media": CS, "Media & Entertainment": CS, "Telecom": CS,
    "Retail": CD, "Restaurants": CD, "Apparel & Luxury": CD, "Autos": CD,
    "Homebuilders & Household Durables": CD, "Hotels, Travel & Leisure": CD, "Leisure Products": CD,
    "Consumer Services": CD,
    "Food & Beverage": ST, "Household & Personal Products": ST, "Tobacco": ST, "Consumer Staples Retail": ST,
    "Oil & Gas": EN, "Coal": EN,
    "Banks": FI, "Insurance": FI, "Capital Markets": FI, "Consumer Finance & Payments": FI,
    "Biotech": HC, "Pharma": HC, "Medical Devices": HC, "Life Sciences & Diagnostics": HC,
    "Health Care Services": HC,
    "Aerospace & Defense": IN, "Machinery & Electrical Equipment": IN, "Construction & Engineering": IN,
    "Transportation": IN, "Commercial & Professional Services": IN, "Distributors": IN,
    "Chemicals": MA, "Metals & Mining": MA, "Paper, Packaging & Building Materials": MA,
    "REITs": RE, "Real Estate Services": RE,
    "Electric Utilities": UT, "Gas & Water Utilities": UT,
}

# (sic_lo, sic_hi, sector, group or None). First match wins.
RULES: list[tuple[int, int, str, str | None]] = [
    # --- specific codes first ---
    (1531, 1531, CD, "Homebuilders & Household Durables"),
    (2080, 2087, ST, "Food & Beverage"),
    (2100, 2199, ST, "Tobacco"),
    (2833, 2834, HC, "Pharma"),
    (2835, 2835, HC, "Life Sciences & Diagnostics"),
    (2836, 2836, HC, "Biotech"),
    (2840, 2844, ST, "Household & Personal Products"),
    (2451, 2452, CD, "Homebuilders & Household Durables"),
    (3011, 3011, CD, "Autos"),
    (3021, 3021, CD, "Apparel & Luxury"),
    (3559, 3559, IN, "Machinery & Electrical Equipment"),
    (3570, 3579, IT, "Tech Hardware"),
    (3630, 3639, CD, "Homebuilders & Household Durables"),
    (3651, 3652, CD, "Homebuilders & Household Durables"),
    (3661, 3669, IT, "Communications Equipment"),
    (3674, 3674, IT, "Semiconductors"),
    (3670, 3679, IT, "Electronic Components & Instruments"),
    (3711, 3716, CD, "Autos"),
    (3720, 3729, IN, "Aerospace & Defense"),
    (3750, 3751, CD, "Autos"),
    (3760, 3769, IN, "Aerospace & Defense"),
    (3790, 3799, CD, "Autos"),
    (3812, 3812, IN, "Aerospace & Defense"),
    (3826, 3826, HC, "Life Sciences & Diagnostics"),
    (3820, 3829, IT, "Electronic Components & Instruments"),
    (3841, 3851, HC, "Medical Devices"),
    (3861, 3861, IT, "Tech Hardware"),
    (3873, 3873, CD, "Apparel & Luxury"),
    (3910, 3915, CD, "Apparel & Luxury"),
    (3940, 3949, CD, "Leisure Products"),
    (4610, 4619, EN, "Oil & Gas"),
    (4810, 4829, CS, "Telecom"),
    (4830, 4841, CS, "Media & Entertainment"),
    (4899, 4899, CS, "Telecom"),
    (4911, 4911, UT, "Electric Utilities"),
    (4922, 4922, EN, "Oil & Gas"),
    (4923, 4924, UT, "Gas & Water Utilities"),
    (4931, 4931, UT, "Electric Utilities"),
    (4932, 4949, UT, "Gas & Water Utilities"),
    (4950, 4959, IN, "Commercial & Professional Services"),
    (4961, 4961, UT, "Gas & Water Utilities"),
    (4991, 4991, UT, "Electric Utilities"),
    (5045, 5045, IT, "Tech Hardware"),
    (5065, 5065, IT, "Electronic Components & Instruments"),
    (5047, 5047, HC, "Health Care Services"),
    (5122, 5122, HC, "Health Care Services"),
    (5140, 5149, ST, "Food & Beverage"),
    (5171, 5172, EN, "Oil & Gas"),
    (5180, 5182, ST, "Food & Beverage"),
    (5331, 5331, ST, "Consumer Staples Retail"),
    (5399, 5399, ST, "Consumer Staples Retail"),
    (5400, 5499, ST, "Consumer Staples Retail"),
    (5912, 5912, ST, "Consumer Staples Retail"),
    (5812, 5813, CD, "Restaurants"),
    (6021, 6036, FI, "Banks"),
    (6324, 6324, HC, "Health Care Services"),
    (6311, 6411, FI, "Insurance"),
    (6798, 6798, RE, "REITs"),
    (7310, 7319, CS, "Media & Entertainment"),
    (7372, 7372, IT, "Software"),
    (7370, 7379, IT, "IT Services"),
    (7800, 7899, CS, "Media & Entertainment"),
    (8731, 8731, HC, "Biotech"),
    (8711, 8711, IN, "Construction & Engineering"),
    # --- broad ranges ---
    (100, 799, ST, "Food & Beverage"),
    (800, 999, MA, "Paper, Packaging & Building Materials"),
    (1000, 1099, MA, "Metals & Mining"),
    (1200, 1299, EN, "Coal"),
    (1300, 1399, EN, "Oil & Gas"),
    (1400, 1499, MA, "Metals & Mining"),
    (1500, 1799, IN, "Construction & Engineering"),
    (2000, 2099, ST, "Food & Beverage"),
    (2200, 2399, CD, "Apparel & Luxury"),
    (2400, 2499, MA, "Paper, Packaging & Building Materials"),
    (2500, 2599, CD, "Homebuilders & Household Durables"),
    (2600, 2699, MA, "Paper, Packaging & Building Materials"),
    (2700, 2799, CS, "Media & Entertainment"),
    (2800, 2899, MA, "Chemicals"),
    (2900, 2999, EN, "Oil & Gas"),
    (3000, 3099, MA, "Chemicals"),
    (3100, 3199, CD, "Apparel & Luxury"),
    (3200, 3299, MA, "Paper, Packaging & Building Materials"),
    (3300, 3399, MA, "Metals & Mining"),
    (3400, 3499, IN, "Machinery & Electrical Equipment"),
    (3500, 3599, IN, "Machinery & Electrical Equipment"),
    (3600, 3699, IN, "Machinery & Electrical Equipment"),
    (3700, 3799, IN, "Machinery & Electrical Equipment"),
    (3800, 3899, IT, "Electronic Components & Instruments"),
    (3900, 3999, IN, "Machinery & Electrical Equipment"),
    (4000, 4799, IN, "Transportation"),
    (4900, 4999, UT, "Electric Utilities"),
    (5000, 5199, IN, "Distributors"),
    (5200, 5999, CD, "Retail"),
    (6000, 6099, FI, "Banks"),
    (6100, 6199, FI, "Consumer Finance & Payments"),
    (6200, 6299, FI, "Capital Markets"),
    (6500, 6599, RE, "Real Estate Services"),
    (6700, 6799, FI, "Capital Markets"),
    (7000, 7099, CD, "Hotels, Travel & Leisure"),
    (7200, 7299, CD, "Consumer Services"),
    (7300, 7399, IN, "Commercial & Professional Services"),
    (7500, 7599, CD, "Consumer Services"),
    (7900, 7999, CD, "Hotels, Travel & Leisure"),
    (8000, 8099, HC, "Health Care Services"),
    (8200, 8299, CD, "Consumer Services"),
    (8100, 8999, IN, "Commercial & Professional Services"),
]

# Large, well-known misfits only: ticker -> (sector, group, reason)
OVERRIDES: dict[str, tuple[str, str, str]] = {
    "GOOGL": (CS, "Interactive Media", "SIC 7370 (computer services); search and video ads business"),
    "GOOG": (CS, "Interactive Media", "SIC 7370; same company as GOOGL"),
    "META": (CS, "Interactive Media", "SIC 7370; social networks and advertising"),
    "PINS": (CS, "Interactive Media", "SIC 7370; advertising-funded social platform"),
    "SNAP": (CS, "Interactive Media", "SIC 7370; advertising-funded social platform"),
    "RDDT": (CS, "Interactive Media", "SIC 7370; advertising-funded social platform"),
    "EA": (CS, "Media & Entertainment", "SIC 7372 (software); video game publisher"),
    "TTWO": (CS, "Media & Entertainment", "SIC 7372; video game publisher"),
    "RBLX": (CS, "Media & Entertainment", "SIC 7372; gaming platform"),
    "DIS": (CS, "Media & Entertainment", "SIC 7990 (amusement); media conglomerate"),
    "LYV": (CS, "Media & Entertainment", "SIC 7900; live entertainment and ticketing"),
    "V": (FI, "Consumer Finance & Payments", "SIC 7389 (business services); card payment network"),
    "MA": (FI, "Consumer Finance & Payments", "SIC 7389; card payment network"),
    "PYPL": (FI, "Consumer Finance & Payments", "SIC 7389; payments"),
    "SPGI": (FI, "Capital Markets", "SIC 7320 (credit reporting); ratings and index provider"),
    "MCO": (FI, "Capital Markets", "SIC 7320; credit ratings"),
    "LRCX": (IT, "Semiconductors", "SIC 3559 (special machinery); wafer-fab equipment"),
    "KLAC": (IT, "Semiconductors", "SIC 3827 (optical instruments); wafer inspection equipment"),
    "HON": (IN, "Machinery & Electrical Equipment", "SIC 3714 (vehicle parts); diversified industrial"),
    "MMM": (IN, "Machinery & Electrical Equipment", "SIC 2670 (converted paper); diversified industrial"),
    "GD": (IN, "Aerospace & Defense", "SIC 3730 (shipbuilding); defense prime"),
    "HII": (IN, "Aerospace & Defense", "SIC 3730; naval shipbuilder for defense"),
    "LHX": (IN, "Aerospace & Defense", "SIC 3663 (communications equipment); defense prime"),
    "TMO": (HC, "Life Sciences & Diagnostics", "SIC 3829 (measuring instruments); life-science tools and services"),
    "DHR": (HC, "Life Sciences & Diagnostics", "SIC 2836 (biologicals); life-science tools and diagnostics"),
    "CVS": (HC, "Health Care Services", "SIC 5912 (drug stores); pharmacy benefits and insurance dominate"),
    "BKNG": (CD, "Hotels, Travel & Leisure", "SIC 4700 (transportation services); online travel"),
    "EXPE": (CD, "Hotels, Travel & Leisure", "SIC 4700; online travel"),
    "ABNB": (CD, "Hotels, Travel & Leisure", "SIC 7370; lodging marketplace"),
    "CCL": (CD, "Hotels, Travel & Leisure", "SIC 4400 (water transportation); cruise line"),
    "RCL": (CD, "Hotels, Travel & Leisure", "SIC 4400; cruise line"),
    "NCLH": (CD, "Hotels, Travel & Leisure", "SIC 4400; cruise line"),
}

KNOWN_MISFITS = [
    "SIC 7370-7379 puts most internet platforms under IT Services; only the largest are overridden to Interactive Media.",
    "SIC 6798 covers every REIT type; data-center, tower and residential REITs are all just 'REITs'.",
    "SIC 2836 (biologicals) and 8731 (commercial research) mix biotech developers with research-tools and CRO companies.",
    "SIC 3559 (special industry machinery) holds both wafer-fab equipment makers and unrelated machinery; only LRCX is overridden.",
    "Conglomerates report one SIC code, so a multi-segment company lands in a single group.",
    "Restaurants (5812) and food retail are split by SIC exactly as GICS splits them; department stores stay in Retail.",
    "Payments companies outside the override list (SIC 7389) fall into Commercial & Professional Services.",
    "A missing or unusual SIC (e.g. 9995 non-operating) leaves the company without a sector; it is counted as 'no data'.",
]


def classify(sic, symbol: str | None = None) -> tuple[str | None, str | None]:
    """(sector, industry_group) for a SIC code and ticker; (None, None) when unmapped."""
    if symbol and symbol in OVERRIDES:
        s, g, _ = OVERRIDES[symbol]
        return s, g
    try:
        code = int(sic)
    except (TypeError, ValueError):
        return None, None
    for lo, hi, sector, group in RULES:
        if lo <= code <= hi:
            return sector, group
    return None, None


def table() -> dict:
    """Serializable mapping for the browser and the docs page."""
    return {"version": MAPPING_VERSION, "sectors": SECTORS, "groups": GROUPS,
            "rules": [list(r) for r in RULES],
            "overrides": {k: list(v) for k, v in OVERRIDES.items()}, "misfits": KNOWN_MISFITS}
