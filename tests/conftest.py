"""Collection scope for the generic StegCore test suite."""
import os

# The pinned-SDK prerelease integration test needs the SDK source checkout that
# .github/workflows/sdk-customer-local-prerelease.yml provides through
# STEGCORE_TEST_LOCAL_SDK_ROOT, and that workflow runs it. Without that
# environment it cannot import, so the generic suite leaves it to its owner.
collect_ignore = []
if not os.environ.get("STEGCORE_TEST_LOCAL_SDK_ROOT"):
    collect_ignore.append("test_sdk_customer_local_prerelease.py")
