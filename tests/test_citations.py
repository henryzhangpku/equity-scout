"""The citation validator keeps only verbatim, number-consistent quotes."""

from scout.narrative import Claim, check_claim, normalize

DOC = ("Revenue for the second quarter was $1.24 billion, up 18% from a year ago, driven by\n"
       "strong demand for our  networking products. Gross margin declined to 41.2% due to\n"
       "higher component costs and an unfavorable product mix. We expect supply constraints\n"
       "to persist through the end of fiscal 2027. The company’s backlog reached a record level.")
DOCS = {"X-8K-ex99": DOC}


def chk(claim, quote, doc_id="X-8K-ex99"):
    return check_claim(Claim(claim=claim, quote=quote, doc_id=doc_id), DOCS)


def test_verbatim_quote_accepted():
    c = chk("Revenue grew 18% year over year.",
            "Revenue for the second quarter was $1.24 billion, up 18% from a year ago")
    assert c.ok, c.reason


def test_whitespace_and_line_breaks_normalised():
    c = chk("Demand for networking products drove growth.",
            "driven by strong demand for our networking products")
    assert c.ok, c.reason


def test_typographic_apostrophe_normalised():
    c = chk("Backlog is at a record.", "The company's backlog reached a record level.")
    assert c.ok, c.reason


def test_paraphrase_rejected():
    c = chk("Margins fell on costs.", "Gross margin fell to 41.2% because of higher component costs")
    assert not c.ok and "not found verbatim" in c.reason


def test_invented_quote_rejected():
    c = chk("Management raised guidance.", "We are raising our full-year guidance for revenue and margin")
    assert not c.ok and "not found verbatim" in c.reason


def test_case_change_rejected():
    c = chk("Revenue grew.", "REVENUE FOR THE SECOND QUARTER WAS $1.24 BILLION")
    assert not c.ok


def test_number_not_in_quote_rejected():
    # the quote is real, but the claim adds a number the quote does not contain
    c = chk("Gross margin fell 300 basis points to 41.2%.",
            "Gross margin declined to 41.2% due to higher component costs")
    assert not c.ok and "300" in c.reason


def test_unknown_document_rejected():
    c = chk("Revenue grew.", "Revenue for the second quarter was $1.24 billion", doc_id="Y-10Q-mdna")
    assert not c.ok and "unknown document" in c.reason


def test_too_short_quote_rejected():
    c = chk("Demand is strong.", "strong demand")
    assert not c.ok and "words" in c.reason


def test_normalize_is_not_fuzzy():
    assert normalize("a — b\n\n c") == "a - b c"
    assert normalize("Gross") != normalize("gross")
