import os
import psycopg2
from governance.access_control import require_tool_allowed
from governance.lineage_logger import log_tool_call


# These are the ONLY queries allowed (menu style)
QUERY_LIBRARY = {
    "get_daily_revenue": """
        SELECT dt, revenue_usd
        FROM lakehouse.gold_daily_revenue
        WHERE dt BETWEEN %s AND %s
        ORDER BY dt;
    """,
    "get_revenue_by_sku": """
        SELECT dt, sku, revenue_usd
        FROM lakehouse.gold_revenue_by_sku_day
        WHERE dt = %s
        ORDER BY revenue_usd DESC;
    """,
    "get_data_freshness": """
        SELECT table_name, latest_ingestion_ts
        FROM lakehouse.gold_data_freshness
        ORDER BY table_name;
    """, "find_missing_skus_yesterday": """
    WITH all_skus AS (
        SELECT DISTINCT sku
        FROM lakehouse.gold_revenue_by_sku_day
        WHERE dt BETWEEN %s AND %s
    ),
    yesterday_skus AS (
        SELECT sku
        FROM lakehouse.gold_revenue_by_sku_day
        WHERE dt = %s
    )
    SELECT a.sku
    FROM all_skus a
    LEFT JOIN yesterday_skus y ON a.sku = y.sku
    WHERE y.sku IS NULL
    ORDER BY a.sku;
    """,
 
}

def get_conn():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "genai_db"),
        user=os.getenv("PGUSER", "genai"),
        password=os.getenv("PGPASSWORD", "genai_password"),
    )

def run_sql(tool_name: str, params: tuple, user_role: str, run_id: str):
    # Permission check
    require_tool_allowed(user_role, tool_name)

    if tool_name not in QUERY_LIBRARY:
        raise ValueError(f"Unknown tool/query: {tool_name}")

    sql = QUERY_LIBRARY[tool_name]

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description]
            result = {"columns": cols, "rows": rows}

            log_tool_call(
               run_id=run_id,
               tool_name=tool_name,
               inputs={"params": params, "user_role": user_role},
               outputs=result
            )

            return result
