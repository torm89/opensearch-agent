from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from discovery_agent.configuration import Configuration
from discovery_agent.prompts.discover import discover_prompt
from discovery_agent.state import HybridState
from discovery_agent.tools.call_open_search import OpenSearchConfig


class Response(BaseModel):
    query: dict = Field(description="The query")


async def discover(state: HybridState, config: RunnableConfig):
    configuration = Configuration.from_runnable_config(config)

    prompt = ChatPromptTemplate.from_messages([
        ('system', discover_prompt),
        ('human',
         """
        - Maximum 15 tool calls per conversation
        - If you must use tools, use them efficiently
        - Have in mind that there can be multiple ways to retrieve data from OpenSearch API and some of them can return empty results while other can return a lot of results
        - First, try to find in the documentation possible ways to retrieve data from OpenSearch API
        """),
        MessagesPlaceholder(variable_name="messages"),
    ])

    action = "Discovering"

    if not state.messages:
        state.messages = [HumanMessage(content=state.question)]

    if state.messages:
        for i, message in enumerate(state.messages):
            if hasattr(message, 'tool_calls'):
                for j, tool_call in enumerate(message.tool_calls):
                    if tool_call['name'] == 'CallOsduSearchService':
                        state.messages[i].tool_calls[j]['args']['opensearch_config'] = None

    chain = prompt | configuration.get_model_large_with_tools()
    response = await configuration.ainvoke_chain(chain, {"messages": state.messages})

    if hasattr(response, "tool_calls") \
            and len(response.tool_calls) > 0 \
            and response.tool_calls[0]['name'] == "CallOsduSearchService":
        opensearch_config = OpenSearchConfig(
            host=configuration.opensearch_host,
            region=configuration.opensearch_region,
            service=configuration.opensearch_service
        )
        response.tool_calls[0]["args"].update({"opensearch_config": opensearch_config})

    if hasattr(response, "tool_calls") and len(response.tool_calls) > 0:
        action = "Using model's tool"

    return {
        "messages": [response],
        "action": action,
    }
