import pytest

# Reuse fixtures from IFU tests inside MOS
# pytest requires this to be top-level
pytest_plugins = [
    "ifu.workflow_test.workflow_fixtures",
]
