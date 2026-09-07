from __future__ import annotations

import argparse

from .create_catalog_search_index import build_catalog_index
from .upload_catalog_data import write_catalog_to_cosmos
from .upload_policy_docs import build_policy_index


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--ai_search_endpoint', required=True)
    p.add_argument('--azure_openai_endpoint', required=True)
    p.add_argument('--embedding_model_name', required=True)
    p.add_argument('--cosmosdb_account', required=True)
    args = p.parse_args()

    build_catalog_index(args.ai_search_endpoint, args.azure_openai_endpoint, args.embedding_model_name)
    build_policy_index(args.ai_search_endpoint, args.azure_openai_endpoint, args.embedding_model_name)
    write_catalog_to_cosmos(args.cosmosdb_account)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
