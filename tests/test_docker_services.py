"""Integration tests — verify Docker-compose services are reachable."""

from __future__ import annotations

import pytest
import requests


pytestmark = pytest.mark.integration


class TestOpenSearch:
    """OpenSearch on port 9200."""

    def test_cluster_health(self, opensearch_ready: None) -> None:
        resp = requests.get("http://localhost:9200/_cluster/health", timeout=5)
        assert resp.status_code == 200
        health = resp.json()
        assert health["status"] in ("green", "yellow"), (
            f"Unexpected cluster status: {health['status']}"
        )


class TestPostgres:
    """Postgres on port 5432."""

    def test_bfsi_database_exists(self, postgres_ready: None) -> None:
        import psycopg2

        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="lecture",
            password="lecture",
            dbname="bfsi",
        )
        cur = conn.cursor()
        cur.execute("SELECT current_database()")
        db_name = cur.fetchone()[0]
        cur.close()
        conn.close()
        assert db_name == "bfsi"


class TestMinIO:
    """MinIO on port 9000."""

    def test_minio_responds(self, minio_ready: None) -> None:
        resp = requests.get(
            "http://localhost:9000/minio/health/live", timeout=5
        )
        assert resp.status_code == 200
