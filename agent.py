import asyncio
import os

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings

async def main() -> None:
    async with MCPServerStreamableHttp(
        name="Streamable HTTP Python Server",
        params={
            "url": "https://nottingham-classifieds-telescope-solid.trycloudflare.com/mcp",
            "timeout": 10,
        },
        cache_tools_list=True,
        max_retry_attempts=3,
    ) as server:
        agent = Agent(
            name="Assistant",
            instructions="Use the MCP tools to answer the questions.",
            mcp_servers=[server],
            model_settings=ModelSettings(tool_choice="required"),
        )

        result = await Runner.run(agent, "Can you get the content of my project with the slug docs?")
        print(result.final_output)

asyncio.run(main())
