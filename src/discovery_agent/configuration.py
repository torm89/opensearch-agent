from __future__ import annotations

import time
from typing import Optional, List

from botocore.exceptions import ClientError
from langchain.chat_models import init_chat_model
from langchain_aws import ChatBedrockConverse
from langchain_core.language_models import LanguageModelLike
from langchain_core.runnables import RunnableConfig, Runnable
from langchain_core.runnables.utils import Input, Output
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from discovery_agent.tools.call_open_search import CallOpenSearchTool


class Configuration(BaseModel):
    opensearch_host: str
    opensearch_region: str
    opensearch_service: str = "es"

    model_large_name: str = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    model_small_name: str = "us.anthropic.claude-3-haiku-20240307-v1:0"

    max_query_count: int = 3
    recursion_limit: int = 3

    @classmethod
    def from_runnable_config(
            cls, config: Optional[RunnableConfig] = None
    ) -> Configuration:
        configurable = (config.get("configurable") or {}) if config else {}
        if configurable.get("osdu_token") and configurable.get("osdu_token").startswith("Bearer "):
            configurable["osdu_token"] = configurable["osdu_token"][7:]

        return cls(**{k: v for k, v in configurable.items() if k in cls.model_fields})

    def model(self):
        return ChatBedrockConverse(
            model_id=self.model_large_name,
            temperature=0,
        )


    def model_by_name(self, model_name: str):
        return ChatBedrockConverse(
            model_id=model_name,
            # temperature=self.temperature,
            # region_name="us-east-2",
        )

    @property
    def model_large(self):
        return init_chat_model(self.model_large_name, model_provider="bedrock_converse")

    @property
    def model_small(self):
        return init_chat_model(self.model_small_name, model_provider="bedrock_converse")

    @staticmethod
    def get_default_tools():
        from discovery_agent.tools.read_from_s3 import ReadDocumentFromS3Tool
        from discovery_agent.tools.search_in_kb import SearchInSchemaDocumentationTool
        from discovery_agent.tools.search_in_kb import SearchInSchemaExamplesTool
        from discovery_agent.tools.search_in_kb import SearchInSearchServiceApiDocumentationTool

        return [
            ReadDocumentFromS3Tool(),
            SearchInSchemaDocumentationTool(),
            SearchInSchemaExamplesTool(),
            SearchInSearchServiceApiDocumentationTool(),
            CallOpenSearchTool(),
        ]

    def get_model_large_with_tools(self, tools: List[BaseTool] = None):
        if tools is None:
            tools = self.get_default_tools()

        return self.model_large.bind_tools(tools)

    def get_model_small_with_tools(self, tools: List[BaseTool] = None):
        if tools is None:
            tools = self.get_default_tools()

        return self.model_small.bind_tools(tools)

    @staticmethod
    async def ainvoke_chain(chain: Runnable, input: Input, config: Optional[RunnableConfig] = None) -> Output:
        max_retries = 15
        wait_time = 10

        for i in range(max_retries):
            try:
                return await chain.ainvoke(input, config)
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code')

                if (i + 1) == max_retries:
                    continue
                elif error_code == 'ThrottlingException':
                    print(f"ThrottlingException ({i}), sleeping for {wait_time} seconds")
                    time.sleep(wait_time)
                else:
                    raise e

        raise Exception("ainvoke_chain failed after 5 attempts")
