"""News items: point-in-time cut at the as-of close, headline + summary only."""

from datetime import date

from scout.data import news as N


def test_news_after_close_is_invisible_and_full_content_never_used(monkeypatch):
    payload = {"news": [
        {"id": 1, "created_at": "2026-10-08T21:30:00Z", "headline": "After the close: guidance cut",
         "summary": "s", "content": "FULL ARTICLE", "symbols": ["XYZ"], "url": "u1", "source": "benzinga"},
        {"id": 2, "created_at": "2026-10-08T15:00:00Z", "headline": "Midday: XYZ wins a large order &amp; more",
         "summary": "XYZ said it won an order.", "content": "FULL ARTICLE", "symbols": ["XYZ"], "url": "u2",
         "source": "benzinga"},
        {"id": 3, "created_at": "2026-10-07T15:00:00Z", "headline": "Ten tickers to watch",
         "summary": "", "symbols": list("ABCDEFGHIJ"), "url": "u3", "source": "benzinga"},
    ]}
    seen = {}

    def fake_fetch(url, **kw):
        seen.update(kw["params"])
        return payload

    monkeypatch.setattr(N, "fetch_json", fake_fetch)
    monkeypatch.setattr(N, "_headers", lambda: {})
    docs = N.AlpacaNews().news("XYZ", date(2026, 10, 8))
    assert seen["end"] == "2026-10-08T20:00:00Z"          # 16:00 New York in October (EDT)
    assert seen["include_content"] == "false"
    assert [d.doc_id for d in docs] == ["XYZ-news-2026-10-08-2"]
    assert docs[0].text == "Midday: XYZ wins a large order & more\nXYZ said it won an order."
    assert "FULL ARTICLE" not in docs[0].text
    assert docs[0].kind == "news" and docs[0].url == "u2"
