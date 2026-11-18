from ingestion.common import allowed_url, canonical_url, url_id
from ingestion.crawl_website import extract_html_content
from guardrails.basic import validate_question, validate_answer


def test_allowed_url():
    assert allowed_url("https://www.tn.gov.in/schemes.php")
    assert allowed_url("https://tn.gov.in/a")
    assert not allowed_url("https://example.com")
    assert not allowed_url("javascript:alert(1)")


def test_canonical_url_preserves_query_order():
    url = "https://www.tn.gov.in/scheme_list.php?dep_id=Mg==&page=2#section"
    assert canonical_url(url) == "https://www.tn.gov.in/scheme_list.php?dep_id=Mg==&page=2"


def test_url_id_stable():
    assert url_id("https://www.tn.gov.in/a") == url_id("https://www.tn.gov.in/a")


def test_extract_html_content():
    html = """
    <html><head><title>Scheme Directory</title></head>
    <body><nav>Navigation</nav><main><h1>Scheme details</h1>
    <p>தமிழ்நாடு அரசு திட்டம்</p>
    <a href="/scheme_list.php?dep_id=Mg==">Schemes</a>
    </main><script>ignore()</script></body></html>
    """
    title, text, links = extract_html_content(html, "https://www.tn.gov.in/")
    assert title == "Scheme Directory"
    assert "தமிழ்நாடு அரசு திட்டம்" in text
    assert "Navigation" not in text
    assert "https://www.tn.gov.in/scheme_list.php?dep_id=Mg==" in links


def test_guardrails():
    validate_question("What schemes are available?")
    validate_answer("Please check the official source.")
