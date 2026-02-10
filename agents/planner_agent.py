import sys
from pathlib import Path

# Ensure imports work when running this file directly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import uuid
from datetime import date, timedelta

from tools.sql_executor import run_sql
from tools.rag_retriever import retrieve_docs
from governance.lineage_logger import log_agent_run


def main():
    print("✅ Agent started...")

    parser = argparse.ArgumentParser()
    parser.add_argument("--role", required=True, choices=["finance", "ops"])
    parser.add_argument("--question", required=True)
    parser.add_argument("--user_id", default="demo_user")
    args = parser.parse_args()

    run_id = str(uuid.uuid4())
    user_role = args.role
    user_id = args.user_id
    question = args.question

    # Log the agent run FIRST (so tool call logs won't violate FK)
    log_agent_run(run_id, user_id, user_role, question)

    yesterday = date.today() - timedelta(days=1)
    last7_start = date.today() - timedelta(days=7)

    sources_used = []
    rag_notes = []  # ✅ always defined

    # 1) Daily revenue (last 7 days)
    daily = run_sql(
        "get_daily_revenue",
        (last7_start, yesterday),
        user_role=user_role,
        run_id=run_id,
    )
    sources_used.append("get_daily_revenue")

    rows = daily["rows"]
    rev_yesterday = float(rows[-1][1])
    rev_prev = float(rows[-2][1])
    drop_pct = ((rev_prev - rev_yesterday) / rev_prev) * 100.0

    # 2) Freshness
    freshness = run_sql(
        "get_data_freshness",
        tuple(),
        user_role=user_role,
        run_id=run_id,
    )
    sources_used.append("get_data_freshness")

    # 2.5) RAG notes (explanations)
    rag_notes = retrieve_docs(
        "common causes of revenue drop, late ingestion, missing SKU feed",
        user_role=user_role,
        top_k=3,
    )
    sources_used.append("retrieve_docs")

    # 3) SKU investigation (finance only)
    sku_allowed = True
    sku_rows = []
    missing_skus = []

    # 3A) SKU revenue tool
    try:
        sku_details = run_sql(
            "get_revenue_by_sku",
            (yesterday,),
            user_role=user_role,
            run_id=run_id,
        )
        sources_used.append("get_revenue_by_sku")
        sku_rows = sku_details["rows"]
    except Exception:
        sku_allowed = False

    # 3B) Missing SKU tool (only if SKU allowed)
    if sku_allowed:
        try:
            missing = run_sql(
                "find_missing_skus_yesterday",
                (last7_start, yesterday - timedelta(days=1), yesterday),
                user_role=user_role,
                run_id=run_id,
            )
            sources_used.append("find_missing_skus_yesterday")
            missing_skus = [r[0] for r in missing["rows"]]
        except Exception:
            missing_skus = []

    # -------- Print Answer --------
    print("\n================= AGENT ANSWER =================")
    print(f"Run ID:   {run_id}")
    print(f"Role:     {user_role}")
    print(f"Question: {question}\n")

    print("1) Revenue trend:")
    print(f"   Yesterday ({yesterday}): ${rev_yesterday:,.2f}")
    print(f"   Day before:              ${rev_prev:,.2f}")
    print(f"   Drop:                    {drop_pct:.1f}%\n")

    print("2) Data freshness (latest ingestion times):")
    for r in freshness["rows"]:
        print(f"   - {r[0]} -> {r[1]}")
    print()

    if sku_allowed:
        print("3) SKU investigation (allowed for your role):")
        if missing_skus:
            print(f"   Missing SKUs yesterday: {', '.join(missing_skus)}")
        else:
            print("   Missing SKUs yesterday: none detected (or tool not enabled).")

        print("\n   Top SKUs yesterday (by revenue):")
        for r in sku_rows[:5]:
            print(f"   - {r[1]}: ${float(r[2]):,.2f}")
        print()
    else:
        print("3) SKU investigation:")
        print("   Not allowed for your role (permission blocked).\n")

    print("4) Notes from documentation (RAG):")
    if not rag_notes:
        print("   No notes retrieved.\n")
    else:
        for note in rag_notes:
            doc = note.get("doc_name")
            chunk = note.get("chunk_id")
            txt = (note.get("text") or "").strip().replace("\n", " ")
            print(f"   - Source: {doc} (chunk {chunk})")
            print(f"     {txt[:220]}...\n")

    print("Sources used (tool calls):")
    for s in sources_used:
        print(f" - {s}")
    print("================================================\n")


if __name__ == "__main__":
    main()
