import os

import boto3
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from opensearchpy import AWSV4SignerAuth, RequestsHttpConnection


def test():
    session = boto3.Session()
    embeddings = BedrockEmbeddings(
        client=session.client("bedrock-runtime", region_name="us-east-1"),
        model_id="amazon.titan-embed-text-v2:0"
    )

    opensearch_url = os.environ.get("OPENSEARCH_URL")
    opensearch_index_name = "knowledge-base-docs"

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

    retriever = vector_store.as_retriever(
        # search_type="mmr",
        # search_type="similarity_score_threshold",
        # search_kwargs={"score_threshold": 0.15}
        search_kwargs={
            "k": 10,
            # "score_threshold": 0.25,
            "filter": {
                "match": {
                    # 'metadata.Markdown Header 1': 'Subdomain'
                    'metadata.filepath': 'query\\'
                }
            },
        },
    )

    docs = retriever.invoke("How many wellbores are located in Poland?")
    for doc in docs:
        # print(doc.page_content)
        print(doc.metadata)
        # print(doc.json())
        # break


if __name__ == "__main__":
    test()
