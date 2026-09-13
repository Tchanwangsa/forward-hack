"""Anthropic client wrapper. One place for the model id, retries and token accounting."""

from anthropic import Anthropic

from asteria.config import settings


def get_client() -> Anthropic:
    return Anthropic(api_key=settings.anthropic_api_key)
