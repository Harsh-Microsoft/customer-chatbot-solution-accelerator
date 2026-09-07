from __future__ import annotations

import argparse
import csv
import os
import sys
from time import sleep
from typing import Any, Dict

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from dotenv import load_dotenv

from scripts.shared.azure_credential_utils import get_azure_credential

# scenario_loader now lives under src/api (the API's Dockerfile build context;
# scripts/ never ships in the container), so it is reached via sys.path here.
_API_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src', 'api')
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from scenario_loader import load_catalog_rows  # noqa: E402

load_dotenv()

CONTAINER_NAME = "catalog"
PARTITION_KEY_PATH = "/productId"


def _get_or_create_database(client: CosmosClient, db_name: str):
    try:
        database = client.create_database_if_not_exists(id=db_name)
        print(f"Database '{db_name}' ready.")
        return database
    except exceptions.CosmosHttpResponseError as e:
        raise SystemExit(f"Error creating database: {e}")


def _get_or_create_container(database, container_name: str, partition_key_path: str):
    try:
        container = database.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path=partition_key_path),
        )
        print(f"Container '{container_name}' ready with partition key '{partition_key_path}'.")
        return container
    except exceptions.CosmosHttpResponseError as e:
        raise SystemExit(f"Error creating container: {e}")


def _normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    item = dict(row)
    for k, v in list(item.items()):
        if isinstance(v, str):
            item[k] = v.strip()

    if not item.get("id"):
        item["id"] = item.get("productId")
    if not item["id"]:
        raise ValueError("Each item must have a unique 'id' or 'productId'.")

    if "Price" in item and item["Price"] != "":
        try:
            item["Price"] = float(item["Price"])
        except ValueError:
            pass
    return item


def _upsert_with_retry(container, item: Dict[str, Any], max_retries: int = 6):
    backoff = 1.0
    for _ in range(max_retries):
        try:
            return container.upsert_item(item)
        except exceptions.CosmosHttpResponseError as e:
            status = getattr(e, "status_code", None)
            if status in (429, 408, 500, 502, 503, 504):
                sleep(backoff)
                backoff = min(backoff * 2, 16)
                continue
            if status in (401, 403):
                raise SystemExit(
                    "Unauthorized. Ensure your identity has 'Cosmos DB Built-in Data Contributor' role."
                ) from e
            raise
    raise RuntimeError(f"Failed to upsert item after {max_retries} retries")


def write_catalog_to_cosmos(cosmosdb_account: str) -> int:
    endpoint = f"https://{cosmosdb_account}.documents.azure.com:443/"
    print(f"Azure Cosmos DB Endpoint: {endpoint}")
    database_name = os.environ.get("AZURE_COSMOSDB_DATABASE", "app_db")

    credential = get_azure_credential()
    client = CosmosClient(endpoint, credential=credential)

    database = _get_or_create_database(client, database_name)
    container = _get_or_create_container(database, CONTAINER_NAME, PARTITION_KEY_PATH)

    csv_path = load_catalog_rows()
    print(f"Importing from '{csv_path}' to container '{CONTAINER_NAME}'...")
    count = 0
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            _upsert_with_retry(container, _normalize_row(row))
            count += 1

    print(f"Done! Upserted {count} documents into '{CONTAINER_NAME}'.")
    return count


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--cosmosdb_account', required=True)
    args = p.parse_args()
    write_catalog_to_cosmos(args.cosmosdb_account)
