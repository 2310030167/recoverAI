import pytest
import httpx
from unittest.mock import patch, MagicMock

from app.schemas.execution import ExecutionRequest, ProviderType, ExecutionState, ProviderScenario
from app.schemas.canonical import ActionType
from app.services.execution.provider import RazorpayPaymentLinkProvider, RazorpayTestModeProvider
from app.services.execution.executor import BoundedRecoveryExecutionEngine
from app.core.config import settings


def test_provider_selection_test_mode(monkeypatch):
    monkeypatch.setattr(settings.execution, "RAZORPAY_PROVIDER_TYPE", "TEST_MODE")
    engine = BoundedRecoveryExecutionEngine()
    assert isinstance(engine.provider, RazorpayTestModeProvider)
    assert engine.provider.provider_name == ProviderType.TEST_MODE


def test_provider_selection_razorpay_payment_link(monkeypatch):
    monkeypatch.setattr(settings.execution, "RAZORPAY_PROVIDER_TYPE", "RAZORPAY_PAYMENT_LINK")
    engine = BoundedRecoveryExecutionEngine()
    assert isinstance(engine.provider, RazorpayPaymentLinkProvider)
    assert engine.provider.provider_name == ProviderType.RAZORPAY_PAYMENT_LINK


def test_missing_credentials_fails_cleanly():
    provider = RazorpayPaymentLinkProvider(key_id="", key_secret="")
    res = provider.execute_action("OPP_TEST_001", ActionType.RETRY, 1000.0, "CUST_001")
    assert res.success is False
    assert res.failure_code == "RAZORPAY_CREDENTIALS_MISSING"
    assert "missing or invalid" in res.failure_reason


def test_invalid_amount_fails_cleanly():
    provider = RazorpayPaymentLinkProvider(key_id="rzp_test_123", key_secret="secret_123")
    res = provider.execute_action("OPP_TEST_001", ActionType.RETRY, -50.0, "CUST_001")
    assert res.success is False
    assert res.failure_code == "INVALID_AMOUNT"


def test_amount_paise_conversion_and_successful_payment_link_creation():
    provider = RazorpayPaymentLinkProvider(key_id="rzp_test_mockkey", key_secret="mocksecret")
    
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": "plink_MockTest123",
        "short_url": "https://rzp.io/i/mocktest123",
        "status": "created",
        "amount": 5427328,
        "currency": "INR"
    }

    with patch("httpx.Client.post", return_value=mock_response) as mock_post:
        res = provider.execute_action(
            opportunity_id="OPP_1930438491",
            action=ActionType.RETRY,
            amount=54273.28,
            customer_id="CUST_0200769623"
        )

        assert res.success is True
        assert res.provider == ProviderType.RAZORPAY_PAYMENT_LINK
        assert res.provider_reference == "plink_MockTest123"
        assert res.execution_state == ExecutionState.SUCCEEDED
        assert res.metadata["payment_link_url"] == "https://rzp.io/i/mocktest123"
        assert res.metadata["payment_status"] == "PENDING"
        assert res.metadata["recovery_status"] == "AWAITING_PAYMENT"

        # Verify exact payload sent to Razorpay API
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        sent_json = call_kwargs[1]["json"]
        sent_auth = call_kwargs[1]["auth"]

        assert sent_json["amount"] == 5427328  # converted ₹54,273.28 float to integer paise
        assert sent_json["currency"] == "INR"
        assert sent_json["reference_id"] == "RECOVERAI_OPP_1930438491"
        assert sent_auth == ("rzp_test_mockkey", "mocksecret")


def test_razorpay_400_bad_request():
    provider = RazorpayPaymentLinkProvider(key_id="rzp_test_mockkey", key_secret="mocksecret")
    
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "error": {
            "code": "BAD_REQUEST_ERROR",
            "description": "Invalid reference_id format"
        }
    }

    with patch("httpx.Client.post", return_value=mock_response):
        res = provider.execute_action("OPP_TEST_400", ActionType.RETRY, 1000.0, "CUST_400")
        assert res.success is False
        assert res.failure_code == "BAD_REQUEST_ERROR"
        assert "Invalid reference_id format" in res.failure_reason


def test_razorpay_401_unauthorized():
    provider = RazorpayPaymentLinkProvider(key_id="rzp_test_invalid", key_secret="wrongsecret")
    
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {
        "error": {
            "code": "UNAUTHORIZED_ERROR",
            "description": "Authentication failed"
        }
    }

    with patch("httpx.Client.post", return_value=mock_response):
        res = provider.execute_action("OPP_TEST_401", ActionType.RETRY, 1000.0, "CUST_401")
        assert res.success is False
        assert res.failure_code == "UNAUTHORIZED_ERROR"


def test_razorpay_timeout():
    provider = RazorpayPaymentLinkProvider(key_id="rzp_test_mockkey", key_secret="mocksecret")

    with patch("httpx.Client.post", side_effect=httpx.TimeoutException("Timeout")):
        res = provider.execute_action("OPP_TEST_TIMEOUT", ActionType.RETRY, 1000.0, "CUST_TIMEOUT")
        assert res.success is False
        assert res.failure_code == "RAZORPAY_TIMEOUT"


def test_execution_engine_integration_with_razorpay_payment_link_provider():
    mock_provider = RazorpayPaymentLinkProvider(key_id="rzp_test_mockkey", key_secret="mocksecret")
    engine = BoundedRecoveryExecutionEngine(provider=mock_provider)

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": "plink_IntegrationTest789",
        "short_url": "https://rzp.io/i/integration789",
        "status": "created"
    }

    with patch("httpx.Client.post", return_value=mock_response):
        req = ExecutionRequest(opportunity_id="OPP_INTEGRATION_001", action=ActionType.RETRY)
        record = engine.execute_opportunity_action(
            request=req,
            amount=25000.0,
            natural_prob=0.35,
            customer_id="CUST_INT_01"
        )

        assert record.execution_status == ExecutionState.SUCCEEDED
        assert record.provider == ProviderType.RAZORPAY_PAYMENT_LINK
        assert record.provider_reference == "plink_IntegrationTest789"
        assert record.metadata["payment_link_url"] == "https://rzp.io/i/integration789"

        # Verify timeline event creation
        timeline = engine.result_processor.get_timeline("OPP_INTEGRATION_001")
        assert len(timeline) == 1
        assert timeline[0].event_type == "PAYMENT_LINK_CREATED"
        assert timeline[0].metadata["payment_link_url"] == "https://rzp.io/i/integration789"


def test_fetch_payment_link_status_and_settlement_flow():
    mock_provider = RazorpayPaymentLinkProvider(key_id="rzp_test_mockkey", key_secret="mocksecret")
    engine = BoundedRecoveryExecutionEngine(provider=mock_provider)

    mock_create_resp = MagicMock()
    mock_create_resp.status_code = 201
    mock_create_resp.json.return_value = {
        "id": "plink_SettlementTest123",
        "short_url": "https://rzp.io/i/settle123",
        "status": "created"
    }

    with patch("httpx.Client.post", return_value=mock_create_resp):
        req = ExecutionRequest(opportunity_id="OPP_SETTLE_001", action=ActionType.RETRY)
        record = engine.execute_opportunity_action(
            request=req,
            amount=89541.27,
            natural_prob=0.35,
            customer_id="CUST_SETTLE_01"
        )
        assert record.execution_status == ExecutionState.SUCCEEDED

    # 1. Sync when status is 'created' (unpaid)
    mock_get_created = MagicMock()
    mock_get_created.status_code = 200
    mock_get_created.json.return_value = {
        "id": "plink_SettlementTest123",
        "status": "created",
        "amount": 8954127,
        "amount_paid": 0,
        "currency": "INR"
    }

    with patch("httpx.Client.get", return_value=mock_get_created):
        sync_res = engine.sync_opportunity_payment("OPP_SETTLE_001")
        assert sync_res["success"] is True
        assert sync_res["is_recovered"] is False
        assert sync_res["payment_status"] == "PENDING"
        assert sync_res["recovery_status"] == "AWAITING_PAYMENT"

    # 2. Sync when status becomes 'paid'
    mock_get_paid = MagicMock()
    mock_get_paid.status_code = 200
    mock_get_paid.json.return_value = {
        "id": "plink_SettlementTest123",
        "status": "paid",
        "amount": 8954127,
        "amount_paid": 8954127,
        "currency": "INR",
        "paid_at": 1756915200
    }

    with patch("httpx.Client.get", return_value=mock_get_paid):
        sync_res_paid = engine.sync_opportunity_payment("OPP_SETTLE_001")
        assert sync_res_paid["success"] is True
        assert sync_res_paid["is_recovered"] is True
        assert sync_res_paid["recovered_amount"] == 89541.27
        assert sync_res_paid["payment_status"] == "PAID"
        assert sync_res_paid["recovery_status"] == "RECOVERED"

        # Verify timeline events (PAYMENT_LINK_CREATED + RECOVERY_OBSERVED)
        timeline = engine.result_processor.get_timeline("OPP_SETTLE_001")
        assert len(timeline) == 2
        assert timeline[0].event_type == "PAYMENT_LINK_CREATED"
        assert timeline[1].event_type == "RECOVERY_OBSERVED"

        # Verify audit trail (PAYMENT_LINK_CREATED_SUCCESS + PAYMENT_RECEIVED_SUCCESS)
        audit = engine.result_processor.get_audit_trail("OPP_SETTLE_001")
        assert len(audit) == 2
        assert audit[1]["event_type"] == "PAYMENT_RECEIVED_SUCCESS"

    # 3. Idempotent re-sync (calling twice does not duplicate events or double count)
    with patch("httpx.Client.get", return_value=mock_get_paid):
        sync_res_repeat = engine.sync_opportunity_payment("OPP_SETTLE_001")
        assert sync_res_repeat["is_recovered"] is True
        assert sync_res_repeat["recovered_amount"] == 89541.27

        # Timeline and audit events count remains 2
        timeline_after = engine.result_processor.get_timeline("OPP_SETTLE_001")
        assert len(timeline_after) == 2


def test_sync_opportunity_payment_idempotency_store_fallback():
    """Verify sync_opportunity_payment resolves records from IdempotencyStore fallback without AttributeError."""
    mock_provider = RazorpayPaymentLinkProvider(key_id="rzp_test_mockkey", key_secret="mocksecret")
    engine = BoundedRecoveryExecutionEngine(provider=mock_provider)

    mock_create_resp = MagicMock()
    mock_create_resp.status_code = 201
    mock_create_resp.json.return_value = {
        "id": "plink_IdemFallback999",
        "short_url": "https://rzp.io/i/fallback999",
        "status": "created"
    }

    with patch("httpx.Client.post", return_value=mock_create_resp):
        req = ExecutionRequest(opportunity_id="OPP_BATCH_0003", action=ActionType.RETRY)
        record = engine.execute_opportunity_action(req, amount=89541.27, natural_prob=0.35, customer_id="CUST_003")

    # Clear in-memory execution_records dict to force fallback to idempotency_store
    engine.execution_records.clear()
    assert len(engine.idempotency_store.get_records_for_opportunity("OPP_BATCH_0003")) == 1

    mock_get_paid = MagicMock()
    mock_get_paid.status_code = 200
    mock_get_paid.json.return_value = {
        "id": "plink_IdemFallback999",
        "status": "paid",
        "amount": 8954127,
        "amount_paid": 8954127,
        "currency": "INR"
    }

    with patch("httpx.Client.get", return_value=mock_get_paid):
        res = engine.sync_opportunity_payment("OPP_BATCH_0003")
        assert res["success"] is True
        assert res["is_recovered"] is True
        assert res["provider_reference"] == "plink_IdemFallback999"
        assert res["recovered_amount"] == 89541.27


def test_fetch_payment_link_by_reference_id_exact_zero_and_multiple():
    provider = RazorpayPaymentLinkProvider(key_id="rzp_test_mockkey", key_secret="mocksecret")

    # 1. Exact match (1 result)
    mock_resp_one = MagicMock()
    mock_resp_one.status_code = 200
    mock_resp_one.json.return_value = {
        "payment_links": [
            {
                "id": "plink_Match111",
                "reference_id": "RECOVERAI_OPP_BATCH_0003",
                "status": "paid",
                "amount": 8954127,
                "short_url": "https://rzp.io/i/match111"
            }
        ]
    }

    with patch("httpx.Client.get", return_value=mock_resp_one):
        res_one = provider.fetch_payment_link_by_reference_id("RECOVERAI_OPP_BATCH_0003")
        assert res_one["success"] is True
        assert res_one["payment_link"]["id"] == "plink_Match111"

    # 2. Zero matches (0 results)
    mock_resp_zero = MagicMock()
    mock_resp_zero.status_code = 200
    mock_resp_zero.json.return_value = {"payment_links": []}

    with patch("httpx.Client.get", return_value=mock_resp_zero):
        res_zero = provider.fetch_payment_link_by_reference_id("RECOVERAI_OPP_BATCH_NONE")
        assert res_zero["success"] is False
        assert res_zero["error_code"] == "PAYMENT_LINK_NOT_FOUND"

    # 3. Multiple exact matches (>1 result)
    mock_resp_multi = MagicMock()
    mock_resp_multi.status_code = 200
    mock_resp_multi.json.return_value = {
        "payment_links": [
            {"id": "plink_Multi1", "reference_id": "RECOVERAI_OPP_DUP"},
            {"id": "plink_Multi2", "reference_id": "RECOVERAI_OPP_DUP"}
        ]
    }

    with patch("httpx.Client.get", return_value=mock_resp_multi):
        res_multi = provider.fetch_payment_link_by_reference_id("RECOVERAI_OPP_DUP")
        assert res_multi["success"] is False
        assert res_multi["error_code"] == "MULTIPLE_PAYMENT_LINKS_FOUND"


def test_provider_reconciliation_after_restart_paid_and_unpaid():
    mock_provider = RazorpayPaymentLinkProvider(key_id="rzp_test_mockkey", key_secret="mocksecret")
    engine = BoundedRecoveryExecutionEngine(provider=mock_provider)

    # Empty all local in-memory stores to simulate fresh backend startup
    engine.execution_records.clear()
    engine.idempotency_store.reset()
    assert len(engine.execution_records) == 0

    # 1. Reconciliation when Razorpay returns status="paid"
    mock_search_paid = MagicMock()
    mock_search_paid.status_code = 200
    mock_search_paid.json.return_value = {
        "payment_links": [
            {
                "id": "plink_ReconPaid888",
                "reference_id": "RECOVERAI_OPP_BATCH_0003",
                "status": "paid",
                "amount": 8954127,
                "short_url": "https://rzp.io/i/reconpaid888",
                "notes": {"opportunity_id": "OPP_BATCH_0003", "action": "RETRY", "customer_id": "CUST_003"}
            }
        ]
    }

    mock_status_paid = MagicMock()
    mock_status_paid.status_code = 200
    mock_status_paid.json.return_value = {
        "id": "plink_ReconPaid888",
        "status": "paid",
        "amount": 8954127,
        "amount_paid": 8954127,
        "currency": "INR",
        "paid_at": 1756915200
    }

    def custom_get(url, **kwargs):
        if "reference_id=" in url:
            return mock_search_paid
        return mock_status_paid

    with patch("httpx.Client.get", side_effect=custom_get):
        sync_res = engine.sync_opportunity_payment("OPP_BATCH_0003")
        assert sync_res["success"] is True
        assert sync_res["is_recovered"] is True
        assert sync_res["recovered_amount"] == 89541.27
        assert sync_res["payment_status"] == "PAID"
        assert sync_res["recovery_status"] == "RECOVERED"
        assert sync_res["provider_reference"] == "plink_ReconPaid888"

    # Verify record was reconstructed & saved in memory
    assert len(engine.execution_records) == 1

    # 2. Idempotent re-sync (calling again does not duplicate events or double count)
    with patch("httpx.Client.get", return_value=mock_status_paid):
        sync_repeat = engine.sync_opportunity_payment("OPP_BATCH_0003")
        assert sync_repeat["is_recovered"] is True
        assert sync_repeat["recovered_amount"] == 89541.27
        timeline = engine.result_processor.get_timeline("OPP_BATCH_0003")
        assert len(timeline) == 1


def test_provider_reconciliation_unpaid():
    mock_provider = RazorpayPaymentLinkProvider(key_id="rzp_test_mockkey", key_secret="mocksecret")
    engine = BoundedRecoveryExecutionEngine(provider=mock_provider)

    engine.execution_records.clear()
    engine.idempotency_store.reset()

    mock_search_created = MagicMock()
    mock_search_created.status_code = 200
    mock_search_created.json.return_value = {
        "payment_links": [
            {
                "id": "plink_ReconCreated777",
                "reference_id": "RECOVERAI_OPP_UNPAID_001",
                "status": "created",
                "amount": 500000,
                "short_url": "https://rzp.io/i/unpaid777",
                "notes": {"opportunity_id": "OPP_UNPAID_001", "action": "REMINDER"}
            }
        ]
    }

    mock_status_created = MagicMock()
    mock_status_created.status_code = 200
    mock_status_created.json.return_value = {
        "id": "plink_ReconCreated777",
        "status": "created",
        "amount": 500000,
        "amount_paid": 0,
        "currency": "INR"
    }

    def custom_get(url, **kwargs):
        if "reference_id=" in url:
            return mock_search_created
        return mock_status_created

    with patch("httpx.Client.get", side_effect=custom_get):
        sync_res = engine.sync_opportunity_payment("OPP_UNPAID_001")
        assert sync_res["success"] is True
        assert sync_res["is_recovered"] is False
        assert sync_res["payment_status"] == "PENDING"
        assert sync_res["recovery_status"] == "AWAITING_PAYMENT"
        assert sync_res["provider_reference"] == "plink_ReconCreated777"
