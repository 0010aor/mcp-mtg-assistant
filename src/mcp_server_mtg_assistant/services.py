import json

import httpx
from mcp import ErrorData, McpError
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS
from pydantic import ValidationError

from .schemas import ScryfallCard


class MtgCardService:
    """Provides methods to interact with the Scryfall API."""

    BASE_URL = 'https://api.scryfall.com'

    def _handle_http_error(self, e: httpx.HTTPStatusError, url: str) -> McpError:
        """Handles HTTP status errors, attempting to parse Scryfall error details."""
        try:
            error_details = e.response.json()
            message = error_details.get('details', f'status code {e.response.status_code}')
            code = INVALID_PARAMS if e.response.status_code in [400, 404] else INTERNAL_ERROR
        except json.JSONDecodeError:
            message = f'status code {e.response.status_code}, response: {e.response.text[:100]}'
            code = INTERNAL_ERROR
        except Exception:
            message = f'status code {e.response.status_code}'
            code = INTERNAL_ERROR
        return McpError(ErrorData(code=code, message=f'Failed Scryfall request ({url}): {message}'))

    def _handle_request_error(self, e: httpx.RequestError) -> McpError:
        """Handles general HTTP request errors."""
        return McpError(ErrorData(code=INTERNAL_ERROR, message=f'Failed Scryfall request ({e.request.url}): {e!r}'))

    def _handle_json_decode_error(self, url: str) -> McpError:
        """Handles JSON decoding errors."""
        return McpError(ErrorData(code=INTERNAL_ERROR, message=f'Failed to decode JSON response from Scryfall ({url})'))

    def _parse_and_validate_response(self, response_json: dict, url: str) -> ScryfallCard:
        """Parses successful response JSON, validates data, and handles Scryfall error objects."""
        if response_json.get('object') == 'list' and response_json.get('data'):
            try:
                return ScryfallCard.model_validate(response_json['data'][0])
            except ValidationError:
                raise McpError(ErrorData(code=INTERNAL_ERROR, message='Failed to parse Scryfall card data'))
        elif response_json.get('object') == 'error':
            message = response_json.get('details', 'Unknown Scryfall error')
            code = INVALID_PARAMS if response_json.get('status') == 404 else INTERNAL_ERROR
            raise McpError(ErrorData(code=code, message=f'Scryfall API error ({url}): {message}'))
        else:
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=f'Unexpected response format from Scryfall ({url})'))

    async def fetch_card(self, query: str) -> ScryfallCard:
        """Searches for cards on Scryfall using the given query and returns the first card found."""
        params = {'q': query}
        search_url = f'{self.BASE_URL}/cards/search'

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(search_url, params=params, timeout=15)
                response.raise_for_status()
                response_json = response.json()
            except httpx.HTTPStatusError as e:
                raise self._handle_http_error(e, search_url)
            except httpx.RequestError as e:
                raise self._handle_request_error(e)
            except json.JSONDecodeError:
                raise self._handle_json_decode_error(search_url)

            return self._parse_and_validate_response(response_json, search_url)
