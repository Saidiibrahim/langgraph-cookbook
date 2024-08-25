#!/usr/bin/env python
import modal
from datetime import datetime
import time
import os
from dotenv import load_dotenv
from graph import graph
from langchain_core.messages import BaseMessage, HumanMessage

load_dotenv()

app = modal.App(name = "JobSearchTeam")

#FIXME: ADD YOUR OWN PATHS HERE
requirements_path = "/Users/ibrahimsaidi/Desktop/Builds/LangGraph_Builds/langgraph-cookbook/requirements.txt"
env_path = "/Users/ibrahimsaidi/Desktop/Builds/LangGraph_Builds/langgraph-cookbook/.env"

graph_image = modal.Image.debian_slim().pip_install_from_requirements(requirements_path)


@app.function(
    image=graph_image,
    schedule = modal.Period(weeks=1),
    secrets=[modal.Secret.from_dotenv(path=env_path)],
    timeout=900
)
def run_graph():
    Job = "Logistics Officer"
    Location = "Adelaide, South Australia"
    query = f"Find job listings for {Job} in {Location}"
    for s in graph.stream(
        {
            "messages": [
                HumanMessage(content=query)
            ]
        }
    ):
        print(s)


app.local_entrypoint()
def run_graph_local():
    Job = "Logistics Officer"
    Location = "Adelaide, South Australia"
    query = f"Find job listings for {Job} in {Location}"
    for s in graph.stream(
        {
            "messages": [
                HumanMessage(content=query)
            ]
        }
    ):
        print(s)

