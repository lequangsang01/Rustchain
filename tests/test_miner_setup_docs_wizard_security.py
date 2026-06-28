from pathlib import Path


WIZARD_HTML = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "miner-setup-wizard"
    / "index.html"
)


def test_remote_node_responses_use_dom_api_not_inner_html():
    """Verify node responses are rendered via DOM API, not innerHTML.

    PR #7725 migrated from innerHTML+escapeHtml to DOM API (createElement,
    textContent, appendChild) which eliminates HTML parser sinks entirely.
    """
    html = WIZARD_HTML.read_text(encoding="utf-8")

    # Raw unescaped patterns must NOT exist
    assert "<pre>${r.text}</pre>" not in html
    assert "<pre>${JSON.stringify(hit,null,2)}</pre>" not in html
    assert "<pre>${String(e)}</pre>" not in html

    # The old escapeHtml-in-template pattern is also removed — replaced by DOM API
    # Neither "${h(r.text)}" nor escapeHtml wrappers should appear in template literals

    # Verify DOM API is used for rendering node responses
    assert "makePillFragment" in html
    assert "createElement" in html
    assert "textContent" in html

    # Verify makePillFragment is called with API response data
    assert "makePillFragment('ok','Reachable', r.text)" in html
    assert "makePillFragment('bad','Failed', r.text" in html
    assert "makePillFragment('ok','Found'" in html
    assert "makePillFragment('bad','Check failed'" in html


def test_generated_command_blocks_use_data_attribute_not_inner_html():
    """Verify command blocks use data-copy attribute, not inline onclick with interpolation."""
    html = WIZARD_HTML.read_text(encoding="utf-8")

    # Raw unescaped patterns must NOT exist
    assert "return `<pre>${cmd}</pre>" not in html
    assert 'onclick="copyText(${JSON.stringify(cmd)})"' not in html

    # The old escapeHtml-in-template pattern is also removed
    # Verify data-copy attribute pattern is used instead
    assert 'data-copy="' in html
    assert "onclick=\"copyText(this.dataset.copy)\"" in html
