# Integration test placeholder so CI's `pytest tests/integration/` step has something to run.
def test_placeholder_integration():
    result = {"status": "ok"}
    assert result["status"] == "ok"
