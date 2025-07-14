import os
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Optional

import boto3
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema
from opensearchpy import AWSV4SignerAuth, RequestsHttpConnection
from pydantic import BaseModel, Field


class SearchInKnowledgeBaseTool(BaseTool, ABC):

    @cached_property
    def boto3_session(self):
        return boto3.Session()

    @cached_property
    def embeddings(self):
        client = self.boto3_session.client("bedrock-runtime", region_name="us-east-1")
        return BedrockEmbeddings(client=client, model_id="amazon.titan-embed-text-v2:0")

    def get_aws_auth(self):
        credentials = self.boto3_session.get_credentials()
        return AWSV4SignerAuth(credentials, "us-east-1", "aoss")

    @property
    def opensearch_url(self):
        return os.environ.get("OPENSEARCH_URL")

    @abstractmethod
    def opensearch_index_name(self):
        raise NotImplementedError

    def get_vector_store(self):
        return OpenSearchVectorSearch(
            opensearch_url=self.opensearch_url,
            index_name=self.opensearch_index_name(),
            embedding_function=self.embeddings,
            http_auth=self.get_aws_auth(),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=300
        )


class SearchInSchemaDocumentationInput(BaseModel):
    phrase: str = Field(description="Phrase to search for (similarity search) in schema documentation")


class SearchInSchemaDocumentationTool(SearchInKnowledgeBaseTool):
    name: str = "SearchInSchemaDocumentation"
    description: str = "Searches for an additional information in the schema documentation"
    args_schema: Optional[ArgsSchema] = SearchInSchemaDocumentationInput
    return_direct: bool = True

    def opensearch_index_name(self):
        return "knowledge-base-docs"

    def _run(
            self, phrase: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        vector_store = self.get_vector_store()
        retriever = vector_store.as_retriever(
            search_kwargs={
                "k": 3,
                "filter": {
                    "match": {
                        'metadata.filepath': 'schemas\\docs\\'
                    }
                },
            }
        )
        docs = retriever.invoke(phrase)

        return "\n\n".join([
            f"""
            <schema_documentation_chunk_context>
            <filepath>{doc.metadata['filepath']}</filepath>
            <chunk_content>{doc.page_content}</chunk_content>
            </schema_documentation_chunk_context>
            """
            for doc in docs
        ])


class SearchInSchemaExamplesInput(BaseModel):
    phrase: str = Field(description="Phrase to search for (similarity search) in schema examples")


class SearchInSchemaExamplesTool(SearchInKnowledgeBaseTool):
    name: str = "SearchInSchemaExamples"
    description: str = "Searches for an additional information from schema examples"
    args_schema: Optional[ArgsSchema] = SearchInSchemaExamplesInput
    return_direct: bool = True

    def opensearch_index_name(self):
        return "knowledge-base-docs-001"

    def _run(
            self, phrase: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        vector_store = self.get_vector_store()
        retriever = vector_store.as_retriever(
            search_kwargs={
                "k": 3,
                "filter": {
                    "match": {
                        'metadata.filepath': 'schemas\\examples\\'
                    }
                },
            }
        )
        docs = retriever.get_relevant_documents(phrase)

        return "\n\n".join([
            f"""
            <schema_examples_chunk_context>
            <filepath>{doc.metadata['filepath']}</filepath>
            <chunk_content>{doc.page_content}</chunk_content>
            </schema_examples_chunk_context>
            """
            for doc in docs
        ])

class SearchInSearchServiceApiDocumentationInput(BaseModel):
    phrase: str = Field(description="Phrase to search for (similarity search) in search service api documentation")


class SearchInSearchServiceApiDocumentationTool(SearchInKnowledgeBaseTool):
    name: str = "SearchInSearchServiceApiDocumentation"
    description: str = "Searches for an additional information from OpenSearch documentation"
    args_schema: Optional[ArgsSchema] = SearchInSchemaExamplesInput
    return_direct: bool = True

    def opensearch_index_name(self):
        return "knowledge-base-docs"

    def _run(
            self, phrase: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        vector_store = self.get_vector_store()
        retriever = vector_store.as_retriever(
            search_kwargs={
                "k": 2,
                "filter": {
                    "match": {
                        'metadata.filepath': 'query\\'
                    }
                },
            }
        )
        docs = retriever.invoke(phrase)

        return "\n\n".join([
            f"""
            <search_service_documentation_chunk_context>
            <filepath>{doc.metadata['filepath']}</filepath>
            <chunk_content>{doc.page_content}</chunk_content>
            </search_service_documentation_chunk_context>
            """
            for doc in docs
        ])
