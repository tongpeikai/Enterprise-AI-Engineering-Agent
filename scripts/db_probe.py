import asyncio
import os

import asyncpg


async def main() -> None:
    conn = await asyncpg.connect(host="127.0.0.1", port=int(os.environ.get("POSTGRES_PORT", "5433")), user=os.environ["POSTGRES_USER"], password=os.environ["POSTGRES_PASSWORD"], database=os.environ["POSTGRES_DB"])
    try:
        extension = await conn.fetchval("SELECT extversion FROM pg_extension WHERE extname='vector'")
        await conn.execute("INSERT INTO stage0_vector_probe(label, embedding) VALUES($1, $2::vector)", "probe", "[1,2,3]")
        row = await conn.fetchrow("SELECT label, embedding::text FROM stage0_vector_probe WHERE label=$1", "probe")
        await conn.execute("DELETE FROM stage0_vector_probe WHERE label=$1", "probe")
        print(f"pgvector={extension} crud={dict(row) if row else None}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
