import os
import pytest
from scripts.nosql_io import load_latest_oltp_json_from_gcs, load_latest_olap_outputs
from scripts.gcp import configure_gcp_credentials

@pytest.fixture(scope="session", autouse=True)
def gcp_setup():
    """
    Configure les credentials GCP une seule fois pour toute la session de test.
    """
    configure_gcp_credentials()
