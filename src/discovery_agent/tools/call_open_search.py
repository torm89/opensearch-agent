from collections import namedtuple
from json import JSONDecodeError
from typing import Optional, Dict, Annotated

import boto3
from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema, InjectedToolArg
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection
from pydantic import BaseModel, Field

OpenSearchConfig = namedtuple("OpenSearchConfig", ["host", "region", "service"], defaults=['', '', 'es'])


class CallOpenSearchInput(BaseModel):
    index: str = Field(description="Index to be used")
    query: Dict = Field(description="Query to be sent to OpenSearch")

    opensearch_config: Annotated[OpenSearchConfig, InjectedToolArg]


class CallOpenSearchTool(BaseTool):
    name: str = "CallOpenSearch"
    description: str = "It calls OpenSearch"
    args_schema: Optional[ArgsSchema] = CallOpenSearchInput
    return_direct: bool = True

    def _run(
            self, index: str, query: Dict, open_search_config: Annotated[OpenSearchConfig, InjectedToolArg],
            run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""

        credentials = boto3.Session().get_credentials()
        auth = AWSV4SignerAuth(credentials, open_search_config.region, open_search_config.service)

        client = OpenSearch(
            hosts=[{'host': open_search_config.host, 'port': 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            pool_maxsize=20
        )

        response = client.search(
            body=query,
            index=index
        )

        try:
            response_json = response.json()
        except JSONDecodeError:
            response_json = None

        return f"""
        <open_search>
        <query>{query}</query>
        <response>
        <status_code>{response.status_code}</status_code>
        <text>{response.text}</text>
        <json>{response_json}</json>
        </response>
        </open_search>
        """
