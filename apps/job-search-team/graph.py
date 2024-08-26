import functools
import operator
from typing import Sequence, TypedDict, Annotated
from utils import create_agent, agent_node, job_search_team_members, llm, supervisor_chain
from tools import (
    EmailSender,
    load_job_search_email_template
    )
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from langgraph.graph import END, StateGraph
import os
from dotenv import load_dotenv

load_dotenv()

tavily_api_key = os.environ["TAVILY_API_KEY"]


email_sender_tool = EmailSender()
email_list = ["ibrahim.aka.ajax@gmail.com"]

tavily_search_tool = TavilySearchResults(max_results=5, api_key=tavily_api_key)



# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str

job_search_agent_prompt = """
You are a web researcher responsible for finding job listings.
"""

job_search_agent = create_agent(llm, [tavily_search_tool], job_search_agent_prompt)
job_search_node = functools.partial(agent_node, agent=job_search_agent, name="JobSearch")

content_designer_agent = create_agent(llm, [load_job_search_email_template], "You are a content designer. Your task is to convert the findings from the job search into html content that can be sent to the user. Use the load_job_search_email_template tool to format the content.")
content_designer_node = functools.partial(agent_node, agent=content_designer_agent, name="ContentDesigner")

content_distributor_agent = create_agent(
    llm,
    [email_sender_tool],
    f"You are a mail distributor. Please distribute the content to the provided email addresses. Always use the email_sender_tool to send the content to the email addresses. The email addresses are: {', '.join(email_list)}",
)
content_distributor_node = functools.partial(agent_node, agent=content_distributor_agent, name="ContentDistributor")

workflow = StateGraph(AgentState)
workflow.add_node("JobSearch", job_search_node)
workflow.add_node("ContentDesigner", content_designer_node)
workflow.add_node("ContentDistributor", content_distributor_node)
workflow.add_node("supervisor", supervisor_chain)

for member in job_search_team_members:
    # We want our workers to ALWAYS "report back" to the supervisor when done
    workflow.add_edge(member, "supervisor")
# The supervisor populates the "next" field in the graph state
# which routes to a node or finishes
conditional_map = {k: k for k in job_search_team_members}
conditional_map["FINISH"] = END
workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
# Finally, add entrypoint
workflow.set_entry_point("supervisor")

graph = workflow.compile()