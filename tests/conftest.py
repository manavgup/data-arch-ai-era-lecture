"""Shared fixtures and pytest configuration for smoke tests."""

from __future__ import annotations

import time

import pytest
import requests


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "integration: requires Docker services")


def _wait_for_service(
    url: str,
    *,
    timeout: int = 60,
    interval: int = 2,
    expected_status: int = 200,
) -> None:
    """Retry an HTTP GET until *url* returns *expected_status* or timeout."""
    deadline = time.time() + timeout
    last_exc: Exception | None = None
    while time.time() < deadline:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == expected_status:
                return
        except requests.ConnectionError as exc:
            last_exc = exc
        time.sleep(interval)
    raise TimeoutError(f"Service at {url} not ready after {timeout}s (last error: {last_exc})")


@pytest.fixture(scope="session")
def opensearch_ready() -> None:
    """Block until OpenSearch cluster health is green or yellow."""
    _wait_for_service("http://localhost:9200/_cluster/health")


@pytest.fixture(scope="session")
def postgres_ready() -> None:
    """Block until Postgres accepts connections on port 5432."""
    import psycopg2

    deadline = time.time() + 60
    last_exc: Exception | None = None
    while time.time() < deadline:
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="lecture",
                password="lecture",
                dbname="bfsi",
            )
            conn.close()
            return
        except psycopg2.OperationalError as exc:
            last_exc = exc
            time.sleep(2)
    raise TimeoutError(f"Postgres not ready after 60s (last error: {last_exc})")


@pytest.fixture(scope="session")
def minio_ready() -> None:
    """Block until MinIO health endpoint responds."""
    _wait_for_service("http://localhost:9000/minio/health/live")
