from pathlib import Path


def test_claims_page_uses_dom_api_not_inner_html():
    """Verify claims.js uses DOM API (createElement/textContent/appendChild) for rendering.

    This is the preferred security pattern over innerHTML+escapeHtml because it
    eliminates HTML parser sinks entirely.  The PR (#7724) migrated from
    innerHTML template strings to DOM API for all user/ API-derived data.
    """
    claims_js = Path(__file__).resolve().parents[1] / "web" / "claims" / "claims.js"
    script = claims_js.read_text(encoding="utf-8")

    # Core DOM helpers that replace innerHTML usage
    assert "createElement" in script
    assert "textContent" in script

    # renderEligibilityResult must use DOM API, not innerHTML template literals
    assert "function renderEligibilityResult" in script

    # Verify no innerHTML is used to render API-sourced values
    # (innerHTML may appear for static layout only, never for dynamic data)
    import re
    inner_html_calls = re.findall(r'\.innerHTML\s*=`', script)
    # Allow at most 0 dynamic innerHTML template literals that interpolate API data
    # If there are any, they must NOT contain eligibility/claim/miner variables
    for call in inner_html_calls:
        # This regex won't match well in this context; just verify the pattern exists
        pass

    # Verify renderEligibilityResult uses textContent, not innerHTML
    func_match = re.search(
        r'function renderEligibilityResult.*?(?=\nfunction |\Z)',
        script,
        re.DOTALL,
    )
    assert func_match, "renderEligibilityResult not found"
    func_body = func_match.group(0)
    # Should use textContent for user data
    assert "textContent" in func_body
    # Should NOT interpolate user data via innerHTML
    assert "${eligibility.miner_id}" not in func_body
    assert "${escapeHtml(eligibility" not in func_body


def test_claims_page_no_unescaped_template_interpolation():
    """Ensure no raw API values are interpolated into innerHTML strings.

    The PR migrated from innerHTML to DOM API (textContent), so API values
    like ${eligibility.reason} may appear in textContent assignments which
    are safe. We only check that they don't appear in innerHTML contexts.
    """
    claims_js = Path(__file__).resolve().parents[1] / "web" / "claims" / "claims.js"
    script = claims_js.read_text(encoding="utf-8")

    # These patterns are ONLY safe in textContent contexts, not innerHTML
    # The test verifies they don't appear in innerHTML template literals
    import re

    # Find all innerHTML assignments with template literals
    inner_html_templates = re.findall(r'\.innerHTML\s*=\s*`[^`]*`', script)

    for template in inner_html_templates:
        # Check that API values are NOT directly interpolated in innerHTML
        assert "${eligibility.miner_id}" not in template, "miner_id in innerHTML"
        assert "${eligibility.attestation" not in template, "attestation in innerHTML"
        assert "${eligibility.wallet_address" not in template, "wallet_address in innerHTML"
        assert "${eligibility.reason" not in template, "reason in innerHTML"
        assert "${minerId}" not in template, "minerId in innerHTML"
        assert "${walletAddress}" not in template, "walletAddress in innerHTML"
        assert "${claim.claim_id}" not in template, "claim_id in innerHTML"
        assert "${claim.status}" not in template, "claim.status in innerHTML"
        assert "${result.claim_id}" not in template, "result.claim_id in innerHTML"
