import hashlib
from typing import Dict, Optional, Any, List
from app.schemas.execution import ExecutionRecordSchema
from app.core.logging import logger


class IdempotencyStore:
    """
    Idempotency & Execution Cache Store for RecoverAI Execution Engine.
    Guarantees that duplicate action execution requests return cached execution records
    without triggering duplicate provider executions.
    """

    def __init__(self):
        self._store: Dict[str, ExecutionRecordSchema] = {}

    def generate_idempotency_key(
        self,
        opportunity_id: str,
        action: str,
        attempt_number: int = 1,
        client_key: Optional[str] = None
    ) -> str:
        """
        Generate deterministic idempotency key.
        """
        if client_key:
            return f"IDEM_{client_key}"

        raw = f"{opportunity_id}:{action}:{attempt_number}"
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12].upper()
        return f"IDEM_{digest}"

    def get(self, idempotency_key: str) -> Optional[ExecutionRecordSchema]:
        """
        Retrieve cached execution record if key exists.
        """
        record = self._store.get(idempotency_key)
        if record:
            logger.info(f"Idempotency Cache HIT for key='{idempotency_key}'. Returning cached execution ID={record.execution_id}.")
        return record

    def put(self, idempotency_key: str, record: ExecutionRecordSchema) -> None:
        """
        Save execution record under idempotency key.
        """
        self._store[idempotency_key] = record
        logger.info(f"Saved execution record ID={record.execution_id} under idempotency key='{idempotency_key}'.")

    def reset(self) -> None:
        """
        Reset idempotency store.
        """
        self._store.clear()
        logger.info("IdempotencyStore reset.")

    def get_records_for_opportunity(self, opportunity_id: str) -> List[ExecutionRecordSchema]:
        """
        Retrieve all cached execution records for a specific opportunity ID.
        """
        return [rec for rec in self._store.values() if rec.opportunity_id == opportunity_id]
