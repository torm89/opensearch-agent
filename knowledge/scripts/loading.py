import json
import os
from pathlib import Path

import boto3
import tqdm
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.documents import Document
from opensearchpy import AWSV4SignerAuth, RequestsHttpConnection


def load_examples():
    session = boto3.Session()
    embeddings = BedrockEmbeddings(
        client=session.client("bedrock-runtime", region_name="us-east-1"),
        model_id="amazon.titan-embed-text-v2:0"
    )

    chunks = []
    with open("chunks_json.json", "r", encoding="utf-8") as file:
        for line in file.readlines():
            chunks.append(Document(**json.loads(line)))

    opensearch_url = os.environ.get("OPENSEARCH_URL")
    opensearch_index_name = "knowledge-base-docs-001"

    print(f"OpenSearch URL: {opensearch_url}")
    print(f"OpenSearch index name: {opensearch_index_name}")

    credentials = session.get_credentials()
    aws_auth = AWSV4SignerAuth(credentials, "us-east-1", "aoss")

    vector_store = OpenSearchVectorSearch(
        opensearch_url=opensearch_url,
        index_name=opensearch_index_name,
        embedding_function=embeddings,
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=300
    )

    batch_size = 500
    for i in range(0, len(chunks), batch_size):
        print(
            f"Processing batch {i // batch_size + 1} of {(len(chunks) + batch_size - 1) // batch_size} (size: {batch_size})")
        batch = chunks[i:i + batch_size]
        vector_store.add_documents(batch)


def load_docs():
    session = boto3.Session()
    embeddings = BedrockEmbeddings(
        client=session.client("bedrock-runtime", region_name="eu-central-1"),
        model_id="amazon.titan-embed-text-v2:0"
    )

    root_path = Path(__file__).parent.parent.parent
    data_path = root_path / "kownledge" / "data"

    chunks = []
    with (data_path / "opensearch_docs_chunks.ndjson" ).open("r", encoding="utf-8") as file:
        for line in file.readlines():
            chunks.append(Document(**json.loads(line)))

    opensearch_url = os.environ.get("OPENSEARCH_URL")
    opensearch_index_name = "opensearch-agent-staging"

    print(f"OpenSearch URL: {opensearch_url}")
    print(f"OpenSearch index name: {opensearch_index_name}")

    credentials = session.get_credentials()
    aws_auth = AWSV4SignerAuth(credentials, "us-east-1", "aoss")

    vector_store = OpenSearchVectorSearch(
        opensearch_url=opensearch_url,
        index_name=opensearch_index_name,
        embedding_function=embeddings,
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=300
    )

    batch_size = 500
    for i in tqdm.tqdm(range(0, len(chunks), batch_size)):
        batch = chunks[i:i + batch_size]
        vector_store.add_documents(batch)


if __name__ == "__main__":
    # load_docs()
    # load_examples()
    pass
