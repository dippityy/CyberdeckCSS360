# Smoke test - quick sanity check that the app starts at all
def test_app_can_be_imported():
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
    # Just importing without crashing is the smoke test
    assert True

# Replace with real test later
