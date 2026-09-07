from __future__ import annotations

import argparse
import os
import re
import sys
import time

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

from scenario_loader import load_manifest, load_policy_docs  # noqa: E402

load_dotenv()


def _create_search_index(search_endpoint, credential, index_name, openai_resource_url, embedding_model):
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
        profiles=[VectorSearchProfile(name="myHnswProfile", algorithm_configuration_name="myHnsw", vectorizer_name="myOpenAI")],
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


def _clean_spaces_with_regex(text):
    cleaned = re.sub(r"\s+", " ", text)
    return re.sub(r"\.{2,}", ".", cleaned)


def _chunk_data(text, tokens_per_chunk=1024):
    text = _clean_spaces_with_regex(text)
    sentences = text.split(". ")
    chunks, current_chunk, current_chunk_token_count = [], "", 0
    for sentence in sentences:
        tokens = sentence.split()
        if current_chunk_token_count + len(tokens) <= tokens_per_chunk:
            current_chunk += (". " if current_chunk else "") + sentence
            current_chunk_token_count += len(tokens)
        else:
            chunks.append(current_chunk)
            current_chunk, current_chunk_token_count = sentence, len(tokens)
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def _get_embedding(text, openai_api_base, openai_api_version, model_name):
    token_provider = get_bearer_token_provider(AzureCliCredential(), "https://cognitiveservices.azure.com/.default")
    client = AzureOpenAI(api_version=openai_api_version, azure_endpoint=openai_api_base, azure_ad_token_provider=token_provider)
    return client.embeddings.create(input=text, model=model_name).data[0].embedding


def build_policy_index(ai_search_endpoint: str, azure_openai_endpoint: str, embedding_model_name: str) -> None:
    manifest = load_manifest()
    index_name = manifest["search"]["policiesIndex"]
    openai_api_version = "2025-01-01-preview"

    credential = get_azure_credential()
    search_index_client = SearchIndexClient(ai_search_endpoint, credential=credential)
    search_index_client.delete_index(index_name)

    _create_search_index(ai_search_endpoint, credential, index_name, azure_openai_endpoint, embedding_model_name)

    search_client = SearchClient(endpoint=ai_search_endpoint, index_name=index_name, credential=credential)

    docs, counter = [], 0
    for doc_path in load_policy_docs():
        text = doc_path.read_text(encoding="utf-8")
        for chunk in _chunk_data(text):
            counter += 1
            try:
                embedding = _get_embedding(chunk, azure_openai_endpoint, openai_api_version, embedding_model_name)
            except Exception:
                time.sleep(30)
                try:
                    embedding = _get_embedding(chunk, azure_openai_endpoint, openai_api_version, embedding_model_name)
                except Exception:
                    embedding = []
            docs.append({"id": str(counter), "content": chunk, "sourceurl": doc_path.name, "contentVector": embedding})
            if len(docs) == 20:
                search_client.upload_documents(documents=docs)
                print(f"{counter} chunks uploaded to Azure Search.")
                docs = []

    if docs:
        search_client.upload_documents(documents=docs)
        print(f"Final {len(docs)} chunks uploaded to Azure Search.")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--ai_search_endpoint', required=True)
    p.add_argument('--azure_openai_endpoint', required=True)
    p.add_argument('--embedding_model_name', required=True)
    args = p.parse_args()
    build_policy_index(args.ai_search_endpoint, args.azure_openai_endpoint, args.embedding_model_name)
