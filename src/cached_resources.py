import guardrails as gd
import streamlit as st
from redisvl.extensions.llmcache import SemanticCache
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor
import redis

from src.models import LLMResponsePostgreSQL, LLMResponseMongoDB
from src.prompt import PROMPT_SQL_POSTGRESQL, PROMPT_NOSQL_MONGODB


@st.cache_resource
def get_guard(format: str) -> gd.Guard:
    """
    Create an output guard using GuardRails.
    """
    if format == "PostgreSQL":
        return gd.Guard.from_pydantic(output_class=LLMResponsePostgreSQL, prompt=PROMPT_SQL_POSTGRESQL)
    elif format == "MongoDB":
        return gd.Guard.from_pydantic(output_class=LLMResponseMongoDB, prompt=PROMPT_NOSQL_MONGODB)
    else:
        raise RuntimeError(f"Unsupported format: {format}")


@st.cache_resource
def instrument() -> None:
    """
    Instrument the OpenAI API using Phoenix.
    """
    tracer_provider = register(
        project_name="my-llm-app",
        endpoint="http://phoenix:6006/v1/traces",
    )
    OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)


@st.cache_resource
def get_semantic_cache(db=0) -> SemanticCache:
    """
    Create a cache using RedisVL SemanticCache.
    """
    llmcache = SemanticCache(
        name="llmcache",
        prefix="llmcache",
        redis_url="redis://redis:6379",
        redis_db=db,
        distance_threshold=0.1,
        overwrite=True,
    )
    return llmcache


@st.cache_resource
def get_exact_match_cache(db=0) -> redis.Redis:
    """
    Create a Redis connection for exact match cache using Redis Hash Map.
    """
    return redis.Redis(host='redis', port=6379, db=db)
