import time

import guardrails as gd
import openai
from pydantic import BaseModel
import streamlit as st

from src.cached_resources import get_guard, instrument, get_exact_match_cache, get_semantic_cache
from src.constants import OPENAI_MODEL_ARGUMENTS
from src.models import LLMResponsePostgreSQL, LLMResponseMongoDB

st.set_page_config(page_title="SQL Code Generator")
st.title("SQL Code Generator")


def generate_response_cached(
        input_text: str,
        cache,
        guard: gd.Guard,
        llm_response: BaseModel,
        distance_threshold: float | None,
        cache_strategy: str
    ) -> None:
    """
    Generate a response for the given input text taking in the cache and guard.
    """
    try:
        start_time = time.time()

        if cache_strategy == "Semantic Cache":
            # Check semantic cache for semantically similar entry
            cached_result = cache.check(
                prompt=input_text,
                distance_threshold=distance_threshold
            )
        else:
            # Simple Redis Hash lookup
            cached_result = cache.get(input_text)
            if cached_result:
                cached_result = [{"response": cached_result.decode("utf-8")}]

        if cached_result:
            # Show cached result
            total_time = time.time() - start_time
            st.info(cached_result[0]["response"])  # Display the cached response
            st.info(f"That query took: {total_time:.2f}s")  # Display the time taken

        else:
            # Run query
            try:
                generated_sql = generate_response(input_text, guard, llm_response)
            except RuntimeError as err:
                st.error(f"Unable to produce an answer due to: {err}")
                return

            total_time = time.time() - start_time
            st.info(generated_sql)
            st.info(f"That query took: {total_time:.2f}s")

            # Store the result in the appropriate cache for future use
            if cache_strategy == "Semantic Cache":
                cache.store(
                    prompt=input_text,
                        response=generated_sql,
                        # Metadata to track when the response was generated
                        metadata={"generated_at": time.time()},
                    )
            else:
                cache.set(input_text, generated_sql)

    except Exception as e:
        st.error(f"Error: {e}")


def generate_response(input_text: str, guard: gd.Guard, llm_response: BaseModel) -> None:
    """
    Generate a response for the given input text.
    """
    (
        _,
        validated_response,
        _,
        validation_passed,
        error,
    ) = guard(
        openai.chat.completions.create,
        prompt_params={
            "query": input_text,
        },
        **OPENAI_MODEL_ARGUMENTS,
    )

    if error or not validation_passed or not validated_response:
        raise RuntimeError(f"Unable to produce an answer due to: {error}")

    valid_sql = llm_response(**validated_response)

    return valid_sql.generated_sql


def main() -> None:
    output_format = st.radio("Ouput format:", ("PostgreSQL", "MongoDB"))
    cache_strategy = st.radio("Select cache strategy:", ("Exact Match Cache", "Semantic Cache"))

    if cache_strategy == "Semantic Cache":
        distance_threshold = st.slider(
            "Select distance threshold for semantic cache:",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.01,
        )
    else:
        distance_threshold = None

    db = 1 if output_format == "MongoDB" else 0
    cache = get_semantic_cache(db) if cache_strategy == "Semantic Cache" else get_exact_match_cache(db)
    guard = get_guard(output_format)
    llm_response = LLMResponseMongoDB if output_format == "MongoDB" else LLMResponsePostgreSQL
    instrument()

    st.warning("This tool uses generative AI and may produce inaccurate or incorrect output", icon="⚠️")
    with st.form("my_form"):
        text = st.text_area(
            "Enter text:",
        )
        submitted = st.form_submit_button("Submit")
        if submitted:
            generate_response_cached(text, cache, guard, llm_response, distance_threshold, cache_strategy)


if __name__ == "__main__":
    main()
