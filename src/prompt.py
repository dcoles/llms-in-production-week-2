PROMPT_SQL_POSTGRESQL = """
Consider a free-form text query for a database.
Your task is to convert the free-form text prompt into an SQL query suitable for
use with the PostgreSQL database system.

Approach the task in a step-by-step basis. Take your time and do not skip any steps:
0. Do not write anything just yet.
1. Read the entirety of the query, making explicit note of the key nouns.
2. Consider what conditions have been requested.
3. Consider what aggregations (if any) have been requested.

Query: ${query}

Only generate SQL code and nothing else.

${gr.complete_json_suffix_v3}
"""


PROMPT_NOSQL_MONGODB = """
Consider a free-form text query for a database.
Your task is to convert the free-form text prompt into a JSON query suitable for
use with MongoDB.

Approach the task in a step-by-step basis. Take your time and do not skip any steps:
0. Do not write anything just yet.
1. Read the entirety of the query, making explicit note of the key nouns.
2. Consider what conditions have been requested.
3. Consider what aggregations (if any) have been requested.

Query: ${query}

Only generate JSON code and nothing else.

${gr.complete_json_suffix_v3}
"""
