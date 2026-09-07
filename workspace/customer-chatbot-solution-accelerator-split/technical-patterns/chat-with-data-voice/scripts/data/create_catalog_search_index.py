from __future__ import annotations

import argparse
import os
import sys
import time

import pandas as pd
from azure.identity import AzureCliCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    AzureOpenAIVectorizer, AzureOpenAIVectorizerParameters,
    HnswAlgorithmConfiguration, SearchField, SearchFieldDataType, SearchIndex,
    SemanticConfiguration, SemanticField, SemanticPrioritizedFields,
    SemanticSearch, VectorSearch, VectorSearchProfile)
from dotenv import load_dotenv
from openai import AzureOpenAI

from scripts.shared.azure_credential_utils import get_azure_credential

# scenario_loader now lives under src/api (the API's Dockerfile build context;
# scripts/ never ships in the container), so it is reached via sys.path here.
_API_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src', 'api')
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from scenario_loader import load_catalog_rows, load_manifest  # noqa: E402

load_dotenv()


def _create_search_index(search_endpoint, credential, index_name, openai_resource_url, embedding_model):
    """Creates or updates a vector + semantic search index for the catalog."""
    index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)

    fields = [
        SearchField(name="id", type=SearchFieldDataType.String, key=True),
        SearchField(name="content", type=SearchFieldDataType.String),
        SearchField(name="sourceurl", type=SearchFieldDataType.String),
        SearchField(
            name="contentVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=1536,
            vector_search_profile_name="myHnswProfile",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
                vectorizer_name="myOpenAI",
            )
        ],
        vectorizers=[
            AzureOpenAIVectorizer(
                vectorizer_name="myOpenAI",
                kind="azureOpenAI",
                parameters=AzureOpenAIVectorizerParameters(
                    resource_url=openai_resource_url,
                    deployment_name=embedding_model,
                    model_name=embedding_model,
                ),
            )
        ],
    )

    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            keywords_fields=[SemanticField(field_name="id")],
            content_fields=[SemanticField(field_name="content")],
        ),
    )

    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=SemanticSearch(configurations=[semantic_config]),
    )

    result = index_client.create_or_update_index(index)
    print(f"Search index '{result.name}' created or updated successfully.")


def _get_embeddings_batch(texts, openai_api_base, openai_api_version, batch_size=50, model_name="text-embedding-3-small"):
    """Gets embeddings for multiple texts in batches, falling back to per-item retries."""
    token_provider = get_bearer_token_provider(AzureCliCredential(), "https://cognitiveservices.azure.com/.default")
    client = AzureOpenAI(
        api_version=openai_api_version,
        azure_endpoint=openai_api_base,
        azure_ad_token_provider=token_provider,
    )

    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            response = client.embeddings.create(input=batch, model=model_name)
            all_embeddings.extend(data.embedding for data in response.data)
        except Exception as e:
            print(f"Batch embedding failed: {e}, retrying individual items...")
            for text in batch:
                try:
                    all_embeddings.append(client.embeddings.create(input=text, model=model_name).data[0].embedding)
                except Exception:
                    all_embeddings.append([])
            time.sleep(1)
    return all_embeddings


def build_catalog_index(ai_search_endpoint: str, azure_openai_endpoint: str, embedding_model_name: str) -> None:
    manifest = load_manifest()
    index_name = manifest["search"]["catalogIndex"]

    credential = get_azure_credential()
    search_index_client = SearchIndexClient(ai_search_endpoint, credential=credential)
    search_index_client.delete_index(index_name)

    _create_search_index(ai_search_endpoint, credential, index_name, azure_openai_endpoint, embedding_model_name)

    search_client = SearchClient(endpoint=ai_search_endpoint, index_name=index_name, credential=credential)

    df_catalog = pd.read_csv(load_catalog_rows())
    all_content, all_ids, all_images = [], [], []
    for _, row in df_catalog.iterrows():
        all_content.append(
            f'productId: {row["productId"]}. ProductName: {row["title"]}. ProductCategory: {row["category"]}. '
            f'Price: {row["price"]}. ProductDescription: {row["description"]}. ProductPunchLine: {row["punchLine"]}. '
            f'ImageURL: {row["image"]}.'
        )
        all_ids.append(row["productId"])
        all_images.append(row["image"])

    print(f"Getting embeddings for {len(all_content)} catalog items in batches...")
    all_embeddings = _get_embeddings_batch(all_content, azure_openai_endpoint, "2025-01-01-preview", model_name=embedding_model_name)

    docs = []
    for i, (content, item_id, image, embedding) in enumerate(zip(all_content, all_ids, all_images, all_embeddings)):
        print(f"Preparing document {i + 1}/{len(all_content)}: id {item_id}")
        docs.append({"id": item_id, "content": content, "sourceurl": image, "contentVector": embedding})
        if len(docs) == 20:
            search_client.upload_documents(documents=docs)
            print(f"{i + 1} documents uploaded to Azure Search.")
            docs = []

    if docs:
        search_client.upload_documents(documents=docs)
        print(f"Final {len(docs)} documents uploaded to Azure Search.")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--ai_search_endpoint', required=True)
    p.add_argument('--azure_openai_endpoint', required=True)
    p.add_argument('--embedding_model_name', required=True)
    args = p.parse_args()
    build_catalog_index(args.ai_search_endpoint, args.azure_openai_endpoint, args.embedding_model_name)
