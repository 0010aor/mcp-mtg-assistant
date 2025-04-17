from mcp import McpError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    ErrorData,
    TextContent,
    Tool,
)

from .formatting import format_card_output
from .schemas import SearchScryfallCardsParams
from .services import MtgCardService


async def serve() -> None:
    """Run the MCP server for fetching data from various APIs."""
    server = Server('mcp-server-fetch')
    card_service = MtgCardService()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name='get_mtg_card_info',
                description='Retrieves details for a specific Magic: The Gathering card from Scryfall (like Oracle text, mana cost, type) when mentioned by name or description in a natural language query.',
                inputSchema=SearchScryfallCardsParams.model_json_schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name, arguments: dict) -> list[TextContent]:
        if name == 'get_mtg_card_info':
            try:
                args = SearchScryfallCardsParams(**arguments)
            except ValueError as e:
                raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

            card_data = await card_service.fetch_card(args.query)
            formatted_output = format_card_output(card_data)
            return [TextContent(type='text', text=formatted_output)]

        else:
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=f'Unknown tool: {name}'))

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        try:
            await server.run(read_stream, write_stream, options, raise_exceptions=True)
        except Exception:
            raise
