from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from discovery_agent.configuration import Configuration
from discovery_agent.nodes.discover import discover
from discovery_agent.nodes.save_question import save_question
from discovery_agent.state import HybridState, InputState

tools = Configuration.get_default_tools()

workflow = StateGraph(HybridState, input=InputState, config_schema=Configuration)

workflow.add_node("save_question", save_question)
workflow.add_node("discover", discover)
workflow.add_node("tools", ToolNode(tools=tools))

workflow.add_conditional_edges("discover", tools_condition)

workflow.add_edge(START, "save_question")
workflow.add_edge("save_question", "discover")
workflow.add_edge("tools", "discover")
workflow.add_edge("discover", END)

graph = workflow.compile()
