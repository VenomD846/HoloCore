from holocore.policy import PrivacyPolicy


def test_privacy_policy_requires_explicit_remote_consent_and_redacts():
    policy = PrivacyPolicy.from_config({"allow_remote": True, "consent": False, "redact_patterns": [r"secret=\w+"]})
    assert policy.remote_allowed is False
    assert policy.redact("secret=abc123") == "[REDACTED]"
    consented = PrivacyPolicy.from_config({"allow_remote": True, "consent": True})
    assert consented.remote_allowed is True
