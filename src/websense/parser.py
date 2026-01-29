"""LLM-based structured data extraction for WebSense."""

from ask2api import Config, generate_api_response, convert_example_to_schema


class Parser:
    """Interfaces with ask2api to extract structured data."""

    def __init__(self, config: Config):
        """Initialize the Parser with ask2api configuration.

        Args:
            config: ask2api Config object for LLM settings.
        """
        self.config = config

    def extract(
        self,
        content: str,
        schema: dict = None,
        example: dict = None,
        truncate: bool = True,
        truncate_length: int = 12000,
        prompt: str | None = None,
    ) -> dict:
        """Extracts structured data from partial content using LLM.

        Args:
            content: The text content to extract data from.
            schema: Optional JSON schema for the output.
            example: Optional JSON example to infer schema from.
            truncate: Whether to truncate the content to a fixed length.
            truncate_length: Max length of content to process.
            prompt: Optional custom extraction prompt.

        Returns:
            Extracted data as a dictionary.

        Raises:
            ValueError: If neither schema nor example is provided.
        """
        if not schema and example:
            schema = convert_example_to_schema(example)
        elif not schema:
            raise ValueError("You must provide either a schema or a JSON example.")

        # Truncate content to avoid token limits (optimistic 12k chars ~ 3-4k tokens)
        if truncate:
            content = content[:truncate_length]

        if not prompt:
            prompt = "Extract structured data from the following webpage content."

        prompt += f"\n\n{content}"

        return generate_api_response(prompt, schema, self.config)
