from typing import Annotated, List, Optional

from pydantic import BaseModel, Field


class SearchScryfallCardsParams(BaseModel):
    """Parameters for searching cards on Scryfall."""

    # See: https://scryfall.com/docs/api/cards/search
    query: Annotated[str, Field(description='The search query string.')]


class CardFace(BaseModel):
    """Represents a single face of a Magic: The Gathering card."""

    name: str
    mana_cost: Optional[str] = None
    type_line: Optional[str] = None
    oracle_text: Optional[str] = None
    power: Optional[str] = None
    toughness: Optional[str] = None


class ScryfallCard(BaseModel):
    """Represents a Magic: The Gathering card object from Scryfall."""

    id: str
    name: str
    mana_cost: Optional[str] = None
    cmc: float = 0.0
    type_line: Optional[str] = None
    oracle_text: Optional[str] = None
    power: Optional[str] = None
    toughness: Optional[str] = None
    card_faces: Optional[List[CardFace]] = None
