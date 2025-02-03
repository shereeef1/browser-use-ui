import asyncio
import os
from dataclasses import dataclass
from typing import List, Optional

import gradio as gr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from browser_use import Agent

load_dotenv()

# Hardcoded API Key
HARD_CODED_API_KEY = "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"  # Replace with your actual API key


@dataclass
class ActionResult:
    is_done: bool
    extracted_content: Optional[str]
    error: Optional[str]
    include_in_memory: bool


@dataclass
class AgentHistoryList:
    all_results: List[ActionResult]
    all_model_outputs: List[dict]


def parse_agent_history(history_str: str) -> None:
    console = Console()

    sections = history_str.split('ActionResult(')

    for i, section in enumerate(sections[1:], 1):
        content = ''
        if 'extracted_content=' in section:
            content = section.split('extracted_content=')[1].split(',')[0].strip("'")

        if content:
            header = Text(f'Step {i}', style='bold blue')
            panel = Panel(content, title=header, border_style='blue')
            console.print(panel)
            console.print()


async def run_browser_task(task: str, model: str = 'gpt-4o', headless: bool = True) -> str:
    os.environ['OPENAI_API_KEY'] = HARD_CODED_API_KEY  # Use hardcoded key

    try:
        agent = Agent(
            task=task,
            llm=ChatOpenAI(model=model),
        )
        result = await agent.run()
        return result
    except Exception as e:
        return f'Error: {str(e)}'


def create_ui():
    with gr.Blocks(title='Browser Use GUI') as interface:
        gr.Markdown('# Browser Use Task Automation')

        with gr.Row():
            with gr.Column():
                task = gr.Textbox(
                    label='Task Description',
                    placeholder='E.g., Find flights from New York to London for next week',
                    lines=3,
                )
                model = gr.Dropdown(
                    choices=['gpt-4', 'gpt-3.5-turbo'], label='Model', value='gpt-4'
                )
                headless = gr.Checkbox(label='Run Headless', value=True)
                submit_btn = gr.Button('Run Task')

            with gr.Column():
                output = gr.Textbox(label='Output', lines=10, interactive=False)

        submit_btn.click(
            fn=lambda *args: asyncio.run(run_browser_task(*args)),
            inputs=[task, model, headless],
            outputs=output,
        )

    return interface


if __name__ == '__main__':
    demo = create_ui()
    demo.launch(share=True)  # Enables public hosting with a Gradio share link
