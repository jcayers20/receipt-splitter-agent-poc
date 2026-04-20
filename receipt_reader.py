import base64
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain.messages import HumanMessage
from langsmith import traceable

from utils import models, tools

load_dotenv()


@traceable(name="Receipt Reader Agent")
def run_agent():
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    # set up agent
    llm = ChatOpenAI(model="gpt-5.4-mini")
    path_to_system_prompt = Path("prompts/receipt_reader.md")
    system_prompt = path_to_system_prompt.read_text()
    agent = create_agent(
        model=llm,
        tools=[tools.categorize_item, tools.perform_calculations],
        system_prompt=system_prompt,
        response_format=ProviderStrategy(models.Receipt),
    )

    # read and encode receipt
    receipt_path = Path("data/pdf/costco_2026_03_27.pdf")
    receipt_b64 = base64.b64encode(receipt_path.read_bytes()).decode("utf-8")

    # invoke agent
    agent_response = agent.invoke(
        input={
            "messages": [
                HumanMessage(
                    content=[
                        {
                            "type": "text",
                            "text": "Please process the attached receipt.",
                        },
                        {
                            "type": "file",
                            "base64": receipt_b64,
                            "mime_type": "application/pdf",
                            "filename": "costco_2024_04_10.pdf",
                        },
                    ]
                )
            ]
        }
    )

    # for tool_call in agent_response["messages"][0]["tool_calls"]:
    #     print(f"Tool call: {tool_call['name']} with arguments {tool_call['arguments']}")

    response = agent_response["structured_response"]

    # write response to JSON
    response_json = response.model_dump_json(indent=4)
    path_to_json_export = Path("target/output.json")
    if not path_to_json_export.parent.exists():
        path_to_json_export.parent.mkdir(parents=True)
    if path_to_json_export.exists():
        print(f"Warning: {path_to_json_export} already exists and will be overwritten.")
    path_to_json_export.write_text(response_json)

    # write item list to CSV
    response_dict = response.model_dump()
    items = response_dict["item_list"]
    item_data = pd.DataFrame(items)
    path_to_csv_export = Path("target/output.csv")
    if not path_to_csv_export.parent.exists():
        path_to_csv_export.parent.mkdir(parents=True)
    if path_to_csv_export.exists():
        print(f"Warning: {path_to_csv_export} already exists and will be overwritten.")
    item_data.to_csv(path_to_csv_export, index=False)


if __name__ == "__main__":
    run_agent()
