from tools.sql_executor import run_sql
from governance.lineage_logger import log_agent_run
from datetime import date, timedelta
import uuid

run_id = str(uuid.uuid4())
user_id = "rohit_test_user"
role_finance = "finance"
role_ops = "ops"

question = "Why did revenue drop yesterday?"
log_agent_run(run_id, user_id, role_finance, question)

yesterday = date.today() - timedelta(days=1)
start = date.today() - timedelta(days=7)
end = yesterday

print("FINANCE: can see SKU details ✅")
print(run_sql("get_revenue_by_sku", (yesterday,), user_role=role_finance, run_id=run_id))

print("\nOPS: should be blocked from SKU details ❌")
try:
    print(run_sql("get_revenue_by_sku", (yesterday,), user_role=role_ops, run_id=run_id))
except Exception as e:
    print("Blocked:", e)

print("\nOPS: can see daily revenue ✅")
print(run_sql("get_daily_revenue", (start, end), user_role=role_ops, run_id=run_id))

print(f"\n✅ Run ID logged: {run_id}")