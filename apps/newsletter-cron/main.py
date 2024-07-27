#!/usr/bin/env python
import modal
from datetime import datetime
import time
import os
from dotenv import load_dotenv
from graph import graph
from langchain_core.messages import BaseMessage, HumanMessage

load_dotenv()

app = modal.App(name = "newsletter-cron")

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
    topic = "Stock Market"
    query = f"Do a thorough research on the latest news on {topic} and distribute the content to the email addresses at your disposal."
    for s in graph.stream(
        {
            "messages": [
                HumanMessage(content=query)
            ]
        }
    ):
        print(s)


if __name__ == "__main__":
    with app.run():
        time.sleep(60)

