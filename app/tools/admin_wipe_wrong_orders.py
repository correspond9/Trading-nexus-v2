"""
Admin utility: archive and wipe top 7 wrongly executed orders.
This file is placed under app/tools so it is available inside the backend container image.
"""
import asyncio
import asyncpg
import csv
import os
from datetime import datetime


async def _table_exists(conn: asyncpg.Connection, table_name: str) -> bool:
    return bool(await conn.fetchval("SELECT to_regclass($1) IS NOT NULL", table_name))


async def main() -> int:
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        # Safe fallback for local/manual usage.
        dsn = "postgresql://postgres:postgres@localhost:5432/trading_terminal"

    conn = await asyncpg.connect(dsn)
    try:
        print("=" * 80)
        print("ADMIN TOOL: Wipe & Archive Wrong Executed Orders")
        print("=" * 80)

        wrong_orders = await conn.fetch(
            """
            SELECT DISTINCT
                pt.order_id,
                pt.user_id,
                pt.symbol,
                pt.side,
                pt.quantity,
                po.limit_price,
                pt.execution_price,
                pt.executed_at,
                pt.position_id,
                pt.trade_id,
                (CASE
                    WHEN pt.side = 'BUY' THEN pt.execution_price - po.limit_price
                    ELSE po.limit_price - pt.execution_price
                END) AS price_deviation
            FROM paper_trades pt
            JOIN paper_orders po ON pt.order_id = po.order_id
            WHERE (
                (pt.side = 'BUY' AND pt.execution_price > po.limit_price) OR
                (pt.side = 'SELL' AND pt.execution_price < po.limit_price)
            )
            ORDER BY pt.executed_at DESC
            LIMIT 7
            """
        )

        if not wrong_orders:
            print("No wrong orders found.")
            return 0

        csv_filename = f"/app/archived_wrong_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "order_id", "user_id", "symbol", "side", "quantity",
                "limit_price", "execution_price", "price_deviation", "executed_at",
                "position_id", "trade_id"
            ])
            for row in wrong_orders:
                writer.writerow([
                    row["order_id"],
                    row["user_id"],
                    row["symbol"],
                    row["side"],
                    row["quantity"],
                    float(row["limit_price"]),
                    float(row["execution_price"]),
                    float(row["price_deviation"]),
                    row["executed_at"],
                    row["position_id"],
                    row["trade_id"],
                ])

        order_ids = [r["order_id"] for r in wrong_orders]
        position_ids = sorted({r["position_id"] for r in wrong_orders if r["position_id"] is not None})

        print(f"Exported archive CSV: {csv_filename}")
        print(f"Deleting {len(order_ids)} orders...")

        if await _table_exists(conn, "paper_order_fills"):
            await conn.execute("DELETE FROM paper_order_fills WHERE order_id = ANY($1)", order_ids)

        if await _table_exists(conn, "execution_log"):
            await conn.execute("DELETE FROM execution_log WHERE order_id = ANY($1)", order_ids)

        await conn.execute("DELETE FROM paper_trades WHERE order_id = ANY($1)", order_ids)
        await conn.execute("DELETE FROM paper_orders WHERE order_id = ANY($1)", order_ids)

        for pos_id in position_ids:
            remaining = await conn.fetchval("SELECT COUNT(*) FROM paper_trades WHERE position_id = $1", pos_id)
            if remaining == 0:
                await conn.execute("DELETE FROM paper_positions WHERE id = $1", pos_id)
                continue

            calc = await conn.fetchrow(
                """
                SELECT
                    SUM(CASE WHEN side='BUY' THEN quantity ELSE -quantity END) AS net_qty,
                    SUM(execution_price * quantity) / NULLIF(SUM(quantity), 0) AS avg_entry
                FROM paper_trades
                WHERE position_id = $1
                """,
                pos_id,
            )
            await conn.execute(
                """
                UPDATE paper_positions
                SET quantity=$1,
                    entry_price=$2,
                    updated_at=now()
                WHERE id=$3
                """,
                int(calc["net_qty"] or 0),
                float(calc["avg_entry"] or 0),
                pos_id,
            )

        print("Wipe complete.")
        print(f"CSV available at: {csv_filename}")
        return 0
    finally:
        await conn.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
