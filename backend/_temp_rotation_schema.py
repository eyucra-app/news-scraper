"""
Schemas para rotación automática del ticker.
"""

from pydantic import BaseModel


class TickerRotationStart(BaseModel):
    """Schema para iniciar rotación automática."""
    interval_seconds: int = 60
    separator_url: str = "https://assets.singular.live/7072b13f9e20b98034f48d6202400ff9/svgs/7esb5NbN8cQxcCk7X0szej_w24h24.svg"
    show_source_name: bool = True
