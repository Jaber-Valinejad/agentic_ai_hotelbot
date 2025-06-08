import os
from dotenv import load_dotenv
load_dotenv()
import openai
from datetime import datetime
from openai import OpenAI
from sqlalchemy import create_engine, text

your_openai_api_key= os.getenv("OPENAI_API_KEY")
NEON_DB_URL= os.getenv("NEON_DB_URL")
engine = create_engine(NEON_DB_URL)


# 2. Define Database Schema and Room Availability Logic
room_schema_sql = '''
CREATE TABLE IF NOT EXISTS rooms (
    room_id SERIAL PRIMARY KEY,
    type TEXT,
    accessibility BOOLEAN,
    base_rate NUMERIC,
    max_occupancy INT
);
'''



# db.execute(room_schema_sql)  # Replace with actual DB execution code

# 3. Parse Natural Language into SQL
def parse_to_sql(nl_query: str) -> str:
    client = OpenAI(api_key=your_openai_api_key)

    prompt = f"""You are an expert SQL generator for a hotel database.
The table is named 'rooms' and has the following columns:
room_id (serial), type (text), accessibility (boolean string: 'TRUE' or 'FALSE'), base_rate (numeric), and max_occupancy (int).
Convert the following natural language query into a valid SQL query.

### Requirements:
- Use only valid SQL syntax.
- Use **ILIKE** instead of **=** for comparing values in the 'type' column to allow case-insensitive matching (e.g., 'delux' should match 'Delux').
- Return **only** the SQL query without any explanations, markdown, or code block.

Natural Language Query: {nl_query}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that only outputs valid SQL. Do not include explanations or markdown."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()

    # Clean up any leftover markdown formatting just in case
    if "```" in sql:
        sql = "\n".join(line for line in sql.splitlines() if not line.strip().startswith("```"))
    if "SELECT" not in sql.upper():
        sql_lines = [line for line in sql.splitlines() if "SELECT" in line.upper()]
        if sql_lines:
            sql = "\n".join(sql_lines)

    return sql

# 4. Validate via CLI and API
def test_nl2sql():
    query = "Show me available deluxe rooms under $500"
    sql = parse_to_sql(query)
    print("Generated SQL:", sql)

#test_nl2sql()

# 5. agnet
class NL2SQLAgent:
    def __init__(self, db_connection):
        self.db = db_connection

    def handle_query(self, query: str):
        try:
            # Convert NL to SQL
            sql = parse_to_sql(query)
            print("Generated SQL:", sql)  # Optional: for debugging
             
            # Execute SQL on Neon
            with self.db.connect() as conn:
                result = conn.execute(text(sql))
                rows = []
                for row in result:
                     print(row)
                     rows.append(row)
                #rows = result.fetchall()
            #return [dict(row) for row in rows]  # Convert to list of dicts
            return [tuple(row) for row in rows]
        except Exception as e:
            return {"error": str(e)}

# Example usage:
agent = NL2SQLAgent(engine)
result = agent.handle_query(" is there any available deluxe rooms under $1000")
print(result)