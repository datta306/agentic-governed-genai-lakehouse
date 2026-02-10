import os
import json
import psycopg2
from datetime import datetime
from typing import Any, Dict, Optional

def get_conn():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "genai_db"),
        user=os.getenv("PGUSER", "genai"),
        password=os.getenv("PGPASSWORD", "genai_password"),
    )

def log_agent_run(run_id: str, user_id: str, user_role: str, question: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO audit.audit_agent_runs (run_id, user_id, user_role, question)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (run_id) DO NOTHING;
                """,
                (run_id, user_id, user_role, question),
            )

def log_tool_call(run_id: str, tool_name: str, inputs: Dict[str, Any], outputs: Dict[str, Any]):
    # Keep outputs small so we don’t store huge results
    safe_outputs = {
        "columns": outputs.get("columns", []),
        "row_count": len(outputs.get("rows", [])),
        "preview_rows": outputs.get("rows", [])[:5],  # only first 5 rows
    }

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO audit.audit_tool_calls (run_id, tool_name, inputs_json, outputs_json)
                VALUES (%s, %s, %s::jsonb, %s::jsonb);
                """,
                (
                    run_id,
                    tool_name,
                    json.dumps(inputs, default=str),
                    json.dumps(safe_outputs, default=str),
                ),
            )
