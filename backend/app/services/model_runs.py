from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.provider import AiResult
from app.db.models import ModelRun


async def record_ai_result(
    session: AsyncSession,
    result: AiResult,
    run_type: str,
    input_ref_type: str,
    input_ref_id: Any | None = None,
    output_ref_type: str | None = None,
    output_ref_id: Any | None = None,
    parameters: dict[str, Any] | None = None,
) -> None:
    if result.status == "skipped":
        return
    now = datetime.now(timezone.utc)
    session.add(
        ModelRun(
            run_type=run_type,
            model_name=result.model_name,
            model_version=result.provider,
            input_ref_type=input_ref_type,
            input_ref_id=input_ref_id,
            output_ref_type=output_ref_type,
            output_ref_id=output_ref_id,
            parameters=parameters or {},
            metrics=result.metrics or {},
            status=result.status,
            error_message=result.error_message,
            started_at=now,
            completed_at=now,
        )
    )
