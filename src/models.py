from guardrails.hub import ValidSQL, ValidJson, UnusualPrompt
from pydantic import BaseModel, Field


class LLMResponsePostgreSQL(BaseModel):
    """
    LLM Response that is validated using Guardrails.ai
    """

    generated_sql: str = Field(
        description="Generate SQL for PostgreSQL given natural language instruction.",
        validators=[
            ValidSQL(on_fail="reask"),
            UnusualPrompt(on="prompt", on_fail="exception")
        ],
    )


class LLMResponseMongoDB(BaseModel):
    """
    LLM Response that is validated using Guardrails.ai
    """

    generated_sql: str = Field(
        description="Generate NoSQL JSON query for MongoDB given natural language instruction.",
        validators=[
            ValidJson(on_fail="reask"),
            UnusualPrompt(on="prompt", on_fail="exception")
        ],
    )
