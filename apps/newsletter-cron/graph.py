import functools
import operator
from typing import Sequence, TypedDict, Annotated
from utils import create_agent, agent_node, members, llm, supervisor_chain
from tools import load_html_template, EmailSender, search, get_contents, find_similar
from langchain_core.messages import BaseMessage
from langgraph.graph import END, StateGraph
from langchain.tools import tool
import os


email_sender_tool = EmailSender()
email_list = ["ibrahim.aka.ajax@gmail.com"]



# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str


research_agent = create_agent(llm, [search, get_contents, find_similar], "You are a web researcher.")
research_node = functools.partial(agent_node, agent=research_agent, name="Researcher")

content_designer_agent = create_agent(llm, [load_html_template], "You are a content designer. Your task is to convert the research output and convert it into html content that can be sent to the user. Always use the load_html_template tool to get the html template.")
content_designer_node = functools.partial(agent_node, agent=content_designer_agent, name="ContentDesigner")

content_distributor_agent = create_agent(
    llm,
    [email_sender_tool],
    f"You are a mail distributor. Please distribute the content to the provided email addresses. Always use the email_sender_tool to send the content to the email addresses. The email addresses are: {', '.join(email_list)}",
)
content_distributor_node = functools.partial(agent_node, agent=content_distributor_agent, name="ContentDistributor")

workflow = StateGraph(AgentState)
workflow.add_node("Researcher", research_node)
workflow.add_node("ContentDesigner", content_designer_node)
workflow.add_node("ContentDistributor", content_distributor_node)
workflow.add_node("supervisor", supervisor_chain)

for member in members:
    # We want our workers to ALWAYS "report back" to the supervisor when done
    workflow.add_edge(member, "supervisor")
# The supervisor populates the "next" field in the graph state
# which routes to a node or finishes
conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END
workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
# Finally, add entrypoint
workflow.set_entry_point("supervisor")

graph = workflow.compile()