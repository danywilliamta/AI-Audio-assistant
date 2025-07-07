import asyncio
import nest_asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import reapy
import asyncio
import json
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import os
import nest_asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI
reapy.connect()
project = reapy.Project()

PRE_PROMPT = (
    "You are a helpful assistant designed to control audio plugins on tracks in a DAW (Digital Audio Workstation). "
    "You can access and manipulate track settings such as EQ, compression, volume, and more through tools. "
    "Your responses must always follow this 3-step structured format using Markdown-style headers:\n\n"
    "**### Thought**\n"
    "Reflect on the user's intent, what information is needed, and what steps should be taken.\n\n"
    "**### Action**\n"
    "Select and call the most appropriate tool based on the current context. Use only the tools provided.\n\n"
    "**### Response**\n"
    "Summarize what has been done or what the next step is, based on the result of the tool call.\n\n"
    "At the beginning of every new conversation or user request, you must start by calling the `get_project_info` tool. "
    "This tool gives you the list of all available tracks, plugins, and their current settings.\n\n"
    "When applying audio FX such as EQ, compression, or reverb, first retrieve mixing best practices from the knowledge base "
    "by calling the appropriate tool (e.g. `get_information_query_chroma`). Use the information from the database as guidance and advice "
    "to apply the most suitable settings for the current context.\n\n"
    "All EQ and frequency values must be normalized between 0.0 and 1.0."
    "Gain values are scaled from -12 dB to +12 dB, and frequency values are log-scaled between 20 Hz and 20,000 Hz."
    "Example: gain_db = 3.0 → normalized_gain = (3.0 + 12) / 24 = 0.625"
    "Example: freq_hz = 60 → normalized_freq = log10(60 / 20) / log10(20000 / 20) ≈ 0.177"
    "Do not make assumptions. Always act based on the actual project state.\n"
    "If any information is missing or unclear, ask follow-up questions.\n"
    "Always aim to be precise, cautious, and helpful.\n"
    "Respond in a clear, readable, concise and structured way."
    "When you're done and there's nothing more to do, always finish with:"
    "##Final answer"
    "Your final response to the user."
    "Never repeat actions after ##Final answer"
)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
N_ITERATIONS_MAX = 8

class MCPOpenAIClient:

    def __init__(self, model: str = "gpt-4o", api_key: str  = None ):
        """Initialize the OpenAI MCP client.

        Args:
            model: The OpenAI model to use.
        """
        if not api_key:
            raise("No api Key set")
        
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openai_client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.stdio: Optional[Any] = None
        self.write: Optional[Any] = None

    async def connect_to_server(self, server_script_path: str = "server.py"):
        """Connect to an MCP server.

        Args:
            server_script_path: Path to the server script.
        """
        # Server configuration
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
        )

        # Connect to the server
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        # Initialize the connection
        await self.session.initialize()

        # List available tools
        # tools_result = await self.session.list_tools()
        # print("\nConnected to server with tools:")
        # for tool in tools_result.tools:
        #     print(f"  - {tool.name}: {tool.description}")
        

    async def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from the MCP server in OpenAI format.

        Returns:
            A list of tools in OpenAI format.
        """
        tools_result = await self.session.list_tools()
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in tools_result.tools
        ]

    async def process_query(self, query: str) -> str:
       
        tools = await self.get_mcp_tools()

        messages = [{"role": "system", "content":PRE_PROMPT}, {"role": "user", "content": query}]
        n = 0
        while n < N_ITERATIONS_MAX:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                temperature=0,
                messages= messages,
                tools=tools,
                tool_choice="auto",
            )           
                
            
            assistant_message = response.choices[0].message
            messages.append(assistant_message)

            if assistant_message.content:
                print("🧠🤖",assistant_message.content)
                if "Final answer" in assistant_message.content:
                    return assistant_message.content
                   
          
            if assistant_message.tool_calls :
                for tool_call in assistant_message.tool_calls:
                    # Execute tool call
                    result = await self.session.call_tool(
                        tool_call.function.name,
                        arguments=json.loads(tool_call.function.arguments),
                    )
                   

                    # Add tool response to conversation
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"✅ Tool '{tool_call.function.name}' executed successfuly Result: {result.content[0].text}"
                        }
                    )          
            
            n+=1
        return "FAILED"
    
    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()
        



async def main():
    """Main entry point for the client."""
    client = MCPOpenAIClient(api_key=api_key)
    await client.connect_to_server("server.py")

    # Example: Ask about company vacation policy
    """Let's start by balancing the volume of my tracks. I want the main lead to sit clearly at the front. Push all of the secondary leads like lead pan right or left extrem or mid slightly, harmonie, behind it in volume and space. Add some stereo width to theses secondary leads by panning it slightly off-center. And adjust the guitar volume assuming this change. """

    """"Apply EQ on all tracks in the session. Each track should have its own EQ tailored to its role: For the lead vocal, make it clear and present in the mix, make sure to  cut around 250–500 Hz For backing vocals (like lead pan, harmonies, doubles), carve out space so they support the lead without clashing—consider slight EQ cuts where the lead is boosted.For guitars, shape them to sit well in the mix without masking vocals. For any other tracks (ambient layers, synths, pads, percussions, etc.), apply appropriate EQ so they fit in the overall balance and don't conflict with the main elements. Make sure nothing is overlooked—every track should be EQed based on its role and frequency content." """
    query = input("🤖 I'm your AI Assistant AUDIO, let's make this track sound fire:")


    response = await client.process_query(query)
    # print(f"\nResponse: {response}")
  
    await client.cleanup()
 

if __name__ == "__main__":
    asyncio.run(main())

