from rfi_watcher.classify import classify_rfi_type


def test_classify_rfi_type_returns_known_label() -> None:
    result = classify_rfi_type("Please clarify the design drawing and engineering specification.")
    assert result.label in {"design", "technical", "general"}
    assert 0.0 <= result.confidence <= 1.0
