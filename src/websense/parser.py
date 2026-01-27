from ask2api import generate_api_response, Config, convert_example_to_schema


class Parser:
    """Interfaces with ask2api to extract structured data."""

    def __init__(self, model: str = None):
        # Allow overriding model via init, else ask2api default or env var
        self.config = Config.from_env()
        if model:
            self.config.model = model

    def extract(self, content: str, schema: dict = None, example: dict = None) -> dict:
        """Extracts structured data from partial content using LLM."""
        if not schema and example:
            schema = convert_example_to_schema(example)
        elif not schema:
            raise ValueError("You must provide either a schema or a JSON example.")

        # Truncate content to avoid token limits (optimistic 12k chars ~ 3-4k tokens)
        truncated_content = content[:12000]

        prompt = f"Extract structured data from the following webpage content:\n\n{truncated_content}"

        return generate_api_response(prompt, schema, self.config)
