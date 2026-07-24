import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func, select

from app.db.models import InventoryItem, RecallMatch
from app.db.session import async_session
from app.services.matching import run_matching
from app.services.seed import seed_company_inventory, seed_recalls


async def main() -> None:
    company_id = sys.argv[1] if len(sys.argv) > 1 else "metro_mart_grocery"
    async with async_session() as session:
        recalls_created = await seed_recalls(session)
        inventory_result = await seed_company_inventory(session, company_id)
        matches = await run_matching(session, min_score=0.35)
        total_matches = await session.scalar(select(func.count(RecallMatch.id)))
        max_exposure = await session.scalar(select(func.max(RecallMatch.exposure_score)))
        sample = await session.scalar(select(RecallMatch).limit(1))
        inventory_location_metadata = await session.scalar(
            select(func.count(InventoryItem.id)).where(InventoryItem.location_type.is_not(None))
        )
        print(
            {
                "recalls_created": recalls_created,
                "company": inventory_result["company"]["name"],
                "inventory_created": inventory_result["created"],
                "matches": matches,
                "total_matches": total_matches,
                "max_exposure": str(max_exposure),
                "sample_exposure_factors_type": type(sample.exposure_factors).__name__ if sample else None,
                "inventory_location_metadata": inventory_location_metadata,
            }
        )


if __name__ == "__main__":
    asyncio.run(main())
