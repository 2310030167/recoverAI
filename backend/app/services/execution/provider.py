import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from app.schemas.execution import ProviderType, ProviderScenario, ExecutionState
from app.schemas.canonical import ActionType
from app.core.logging import logger


class ProviderExecutionResult:
    def __init__(
        self,
        success: bool,
        provider: ProviderType,
        provider_reference: Optional[str] = None,
        failure_code: Optional[str] = None,
        failure_reason: Optional[str] = None,
        execution_state: ExecutionState = ExecutionState.SUCCEEDED,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.provider = provider
        self.provider_reference = provider_reference
        self.failure_code = failure_code
        self.failure_reason = failure_reason
        self.execution_state = execution_state
        self.metadata = metadata or {}


class BaseExecutionProvider(ABC):
    @abstractmethod
    def execute_action(
        self,
        opportunity_id: str,
        action: ActionType,
        amount: float,
        customer_id: str,
        scenario: ProviderScenario = ProviderScenario.SUCCESS
    ) -> ProviderExecutionResult:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def fetch_payment_link_status(self, plink_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def fetch_payment_link_by_reference_id(self, reference_id: str) -> Dict[str, Any]:
        pass


class RazorpayTestModeProvider(BaseExecutionProvider):
    """
    Razorpay Test-Mode Provider Abstraction.
    Simulates notification, gateway retry, and escalation execution without real financial transactions.
    Supports deterministic scenario simulation (SUCCESS, TEMPORARY_FAILURE, PERMANENT_FAILURE, TIMEOUT, ALREADY_PROCESSED, BLOCKED).
    """

    def __init__(self):
        self.provider_name = ProviderType.TEST_MODE
        self.execution_log: Dict[str, Any] = {}

    def reset(self) -> None:
        """Reset provider state and execution logs."""
        self.execution_log.clear()
        logger.info("RazorpayTestModeProvider state reset.")

    def fetch_payment_link_status(self, plink_id: str) -> Dict[str, Any]:
        """Simulated payment link status fetch for test mode."""
        is_paid = "PAID" in plink_id.upper() or plink_id in self.execution_log
        return {
            "success": True,
            "id": plink_id,
            "status": "paid" if is_paid else "created",
            "amount": 100000,
            "amount_paid": 100000 if is_paid else 0,
            "currency": "INR",
            "reference_id": f"RECOVERAI_TEST_{plink_id}"
        }

    def fetch_payment_link_by_reference_id(self, reference_id: str) -> Dict[str, Any]:
        """Simulated payment link lookup by reference_id for test mode."""
        for plink_id, rec in self.execution_log.items():
            if getattr(rec, "metadata", {}).get("razorpay_reference_id") == reference_id or reference_id in plink_id:
                return {
                    "success": True,
                    "payment_link": {
                        "id": plink_id,
                        "reference_id": reference_id,
                        "status": "created",
                        "amount": 100000,
                        "short_url": f"https://rzp.io/i/{plink_id}",
                        "notes": {"opportunity_id": reference_id.replace("RECOVERAI_", ""), "action": "RETRY"}
                    }
                }
        return {
            "success": False,
            "error_code": "PAYMENT_LINK_NOT_FOUND",
            "error_message": f"No Payment Link found matching reference_id={reference_id}."
        }

    def execute_action(
        self,
        opportunity_id: str,
        action: ActionType,
        amount: float,
        customer_id: str,
        scenario: ProviderScenario = ProviderScenario.SUCCESS
    ) -> ProviderExecutionResult:
        """
        Execute bounded action through appropriate test pathway.
        """
        ref_id = f"PAYOUT_TEST_{uuid.uuid4().hex[:8].upper()}"

        logger.info(
            f"Test-Mode Provider Executing Action '{action.value}' for Opportunity ID={opportunity_id} "
            f"under Scenario='{scenario.value}' (Ref={ref_id})"
        )

        if scenario == ProviderScenario.SUCCESS:
            result = ProviderExecutionResult(
                success=True,
                provider=self.provider_name,
                provider_reference=ref_id,
                execution_state=ExecutionState.SUCCEEDED,
                metadata={"action": action.value, "amount": amount, "customer_id": customer_id}
            )
        elif scenario == ProviderScenario.TEMPORARY_FAILURE:
            result = ProviderExecutionResult(
                success=False,
                provider=self.provider_name,
                provider_reference=ref_id,
                failure_code="GATEWAY_TEMPORARY_DOWN",
                failure_reason="Razorpay test gateway temporary connection timeout.",
                execution_state=ExecutionState.FAILED
            )
        elif scenario == ProviderScenario.PERMANENT_FAILURE:
            result = ProviderExecutionResult(
                success=False,
                provider=self.provider_name,
                provider_reference=ref_id,
                failure_code="CARD_EXPIRED_PERMANENT",
                failure_reason="Customer payment method permanently invalidated or expired.",
                execution_state=ExecutionState.FAILED
            )
        elif scenario == ProviderScenario.TIMEOUT:
            result = ProviderExecutionResult(
                success=False,
                provider=self.provider_name,
                provider_reference=ref_id,
                failure_code="PROVIDER_TIMEOUT",
                failure_reason="Provider execution timed out after 3000ms.",
                execution_state=ExecutionState.FAILED
            )
        elif scenario == ProviderScenario.ALREADY_PROCESSED:
            result = ProviderExecutionResult(
                success=True,
                provider=self.provider_name,
                provider_reference=ref_id,
                execution_state=ExecutionState.SUCCEEDED,
                metadata={"note": "Already processed by external gateway"}
            )
        elif scenario == ProviderScenario.BLOCKED:
            result = ProviderExecutionResult(
                success=False,
                provider=self.provider_name,
                provider_reference=ref_id,
                failure_code="PROVIDER_POLICY_BLOCKED",
                failure_reason="Provider internal compliance filter blocked action.",
                execution_state=ExecutionState.BLOCKED
            )
        else:
            result = ProviderExecutionResult(
                success=True,
                provider=self.provider_name,
                provider_reference=ref_id,
                execution_state=ExecutionState.SUCCEEDED
            )

        self.execution_log[ref_id] = result
        return result


class RazorpayPaymentLinkProvider(BaseExecutionProvider):
    """
    Razorpay Payment Links Provider (Test Mode API).
    Calls POST https://api.razorpay.com/v1/payment_links using HTTP Basic Auth (key_id, key_secret).
    Maps RecoverAI execution requests into inbound payment collection links for overdue invoices.
    """

    def __init__(self, key_id: Optional[str] = None, key_secret: Optional[str] = None):
        from app.core.config import settings
        self.provider_name = ProviderType.RAZORPAY_PAYMENT_LINK
        self.key_id = key_id if key_id is not None else getattr(settings.execution, "RAZORPAY_KEY_ID", "")
        self.key_secret = key_secret if key_secret is not None else getattr(settings.execution, "RAZORPAY_KEY_SECRET", "")
        self.execution_log: Dict[str, Any] = {}

    def reset(self) -> None:
        """Reset execution log store."""
        self.execution_log.clear()
        logger.info("RazorpayPaymentLinkProvider state reset.")

    def execute_action(
        self,
        opportunity_id: str,
        action: ActionType,
        amount: float,
        customer_id: str,
        scenario: ProviderScenario = ProviderScenario.SUCCESS
    ) -> ProviderExecutionResult:
        """
        Execute payment collection link creation via Razorpay Payment Links API.
        """
        import httpx

        if not self.key_id or not self.key_secret:
            logger.error("Razorpay Payment Links Provider execution failed: Missing RAZORPAY_KEY_ID or RAZORPAY_KEY_SECRET credentials.")
            return ProviderExecutionResult(
                success=False,
                provider=self.provider_name,
                failure_code="RAZORPAY_CREDENTIALS_MISSING",
                failure_reason="Razorpay API credentials (RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET) are missing or invalid.",
                execution_state=ExecutionState.FAILED
            )

        if amount <= 0:
            logger.error(f"Razorpay Payment Link creation rejected: Amount must be > 0. Received: {amount}")
            return ProviderExecutionResult(
                success=False,
                provider=self.provider_name,
                failure_code="INVALID_AMOUNT",
                failure_reason=f"Payment link amount must be greater than 0. Received amount: ₹{amount}",
                execution_state=ExecutionState.FAILED
            )

        # Convert INR amount (float) to paise (integer)
        amount_paise = int(round(amount * 100))
        ref_id = f"RECOVERAI_{opportunity_id}"

        payload: Dict[str, Any] = {
            "amount": amount_paise,
            "currency": "INR",
            "accept_partial": False,
            "reference_id": ref_id,
            "description": f"RecoverAI Invoice Recovery Payment ({opportunity_id})",
            "notes": {
                "opportunity_id": opportunity_id,
                "action": action.value,
                "customer_id": customer_id
            }
        }

        url = "https://api.razorpay.com/v1/payment_links"

        try:
            logger.info(f"Posting to Razorpay Payment Links API (Ref={ref_id}, Amount={amount_paise} paise)")
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    url,
                    json=payload,
                    auth=(self.key_id, self.key_secret)
                )

            if resp.status_code in (200, 201):
                data = resp.json()
                plink_id = data.get("id", f"plink_{uuid.uuid4().hex[:8]}")
                short_url = data.get("short_url", f"https://rzp.io/i/{uuid.uuid4().hex[:6]}")

                result = ProviderExecutionResult(
                    success=True,
                    provider=self.provider_name,
                    provider_reference=plink_id,
                    execution_state=ExecutionState.SUCCEEDED,
                    metadata={
                        "payment_link_url": short_url,
                        "payment_status": "PENDING",
                        "recovery_status": "AWAITING_PAYMENT",
                        "action": action.value,
                        "amount": amount,
                        "customer_id": customer_id,
                        "invoice_id": opportunity_id,
                        "razorpay_reference_id": ref_id
                    }
                )
                self.execution_log[plink_id] = result
                logger.info(f"Razorpay Payment Link Created: ID={plink_id}, URL={short_url}")
                return result
            else:
                try:
                    err_json = resp.json()
                    err_code = err_json.get("error", {}).get("code", f"RAZORPAY_HTTP_{resp.status_code}")
                    err_msg = err_json.get("error", {}).get("description", resp.text[:200])
                except Exception:
                    err_code = f"RAZORPAY_HTTP_{resp.status_code}"
                    err_msg = resp.text[:200]

                logger.error(f"Razorpay API Error Response ({resp.status_code}): {err_msg}")
                return ProviderExecutionResult(
                    success=False,
                    provider=self.provider_name,
                    failure_code=str(err_code),
                    failure_reason=f"Razorpay API returned HTTP {resp.status_code}: {err_msg}",
                    execution_state=ExecutionState.FAILED
                )
        except httpx.TimeoutException:
            logger.error("Razorpay API request timed out after 10000ms.")
            return ProviderExecutionResult(
                success=False,
                provider=self.provider_name,
                failure_code="RAZORPAY_TIMEOUT",
                failure_reason="Connection to Razorpay Payment Links API timed out.",
                execution_state=ExecutionState.FAILED
            )
        except Exception as e:
            logger.error(f"Failed to execute Razorpay Payment Links API call: {str(e)}")
            return ProviderExecutionResult(
                success=False,
                provider=self.provider_name,
                failure_code="RAZORPAY_CONNECTION_ERROR",
                failure_reason=f"Failed to connect to Razorpay API: {str(e)}",
                execution_state=ExecutionState.FAILED
            )

    def fetch_payment_link_status(self, plink_id: str) -> Dict[str, Any]:
        """
        Fetch status of a payment link from Razorpay API.
        Calls GET https://api.razorpay.com/v1/payment_links/{plink_id} using HTTP Basic Auth.
        """
        import httpx

        if not self.key_id or not self.key_secret:
            logger.error("Razorpay Payment Links status fetch failed: Missing credentials.")
            return {
                "success": False,
                "error_code": "RAZORPAY_CREDENTIALS_MISSING",
                "error_message": "Razorpay API credentials (RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET) are missing."
            }

        url = f"https://api.razorpay.com/v1/payment_links/{plink_id}"

        try:
            logger.info(f"Fetching Razorpay Payment Link Status for ID={plink_id}")
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(url, auth=(self.key_id, self.key_secret))

            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Razorpay Payment Link status returned: ID={plink_id}, Status={data.get('status')}")
                return {
                    "success": True,
                    "id": data.get("id", plink_id),
                    "status": data.get("status", "created"),
                    "amount": data.get("amount", 0),
                    "amount_paid": data.get("amount_paid", 0),
                    "currency": data.get("currency", "INR"),
                    "paid_at": data.get("paid_at"),
                    "reference_id": data.get("reference_id"),
                    "short_url": data.get("short_url")
                }
            else:
                try:
                    err_json = resp.json()
                    err_msg = err_json.get("error", {}).get("description", resp.text[:200])
                except Exception:
                    err_msg = resp.text[:200]

                logger.error(f"Razorpay API Error Response ({resp.status_code}): {err_msg}")
                return {
                    "success": False,
                    "error_code": f"RAZORPAY_HTTP_{resp.status_code}",
                    "error_message": f"Razorpay API returned HTTP {resp.status_code}: {err_msg}"
                }
        except httpx.TimeoutException:
            logger.error(f"Razorpay API request timed out for status fetch of ID={plink_id}")
            return {
                "success": False,
                "error_code": "RAZORPAY_TIMEOUT",
                "error_message": "Connection to Razorpay Payment Links API timed out."
            }
        except Exception as e:
            logger.error(f"Failed to fetch Razorpay Payment Link status: {str(e)}")
            return {
                "success": False,
                "error_code": "RAZORPAY_CONNECTION_ERROR",
                "error_message": f"Failed to connect to Razorpay API: {str(e)}"
            }

    def fetch_payment_link_by_reference_id(self, reference_id: str) -> Dict[str, Any]:
        """
        Fetch Payment Link by user-defined reference_id from Razorpay API.
        Calls GET https://api.razorpay.com/v1/payment_links/?reference_id={reference_id} using Basic Auth.
        """
        import httpx

        if not self.key_id or not self.key_secret:
            logger.error("Razorpay Payment Links search failed: Missing credentials.")
            return {
                "success": False,
                "error_code": "RAZORPAY_CREDENTIALS_MISSING",
                "error_message": "Razorpay API credentials (RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET) are missing."
            }

        url = f"https://api.razorpay.com/v1/payment_links/?reference_id={reference_id}"

        try:
            logger.info(f"Querying Razorpay Payment Links API for reference_id={reference_id}")
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(url, auth=(self.key_id, self.key_secret))

            if resp.status_code == 200:
                data = resp.json()
                items = data.get("payment_links", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
                
                # Filter for exact reference_id equality
                matches = [item for item in items if isinstance(item, dict) and item.get("reference_id") == reference_id]
                
                if len(matches) == 0:
                    logger.info(f"Razorpay Payment Link query returned 0 matches for reference_id={reference_id}")
                    return {
                        "success": False,
                        "error_code": "PAYMENT_LINK_NOT_FOUND",
                        "error_message": f"No Razorpay Payment Link found matching reference_id={reference_id}."
                    }
                elif len(matches) == 1:
                    plink = matches[0]
                    logger.info(f"Razorpay Payment Link correlated: reference_id={reference_id} -> ID={plink.get('id')}, Status={plink.get('status')}")
                    return {
                        "success": True,
                        "payment_link": plink
                    }
                else:
                    logger.error(f"Ambiguity error: Multiple ({len(matches)}) Razorpay Payment Links matched reference_id={reference_id}")
                    return {
                        "success": False,
                        "error_code": "MULTIPLE_PAYMENT_LINKS_FOUND",
                        "error_message": f"Multiple ({len(matches)}) Payment Links found matching reference_id={reference_id}."
                    }
            else:
                try:
                    err_json = resp.json()
                    err_msg = err_json.get("error", {}).get("description", resp.text[:200])
                except Exception:
                    err_msg = resp.text[:200]

                logger.error(f"Razorpay API Search Error Response ({resp.status_code}): {err_msg}")
                return {
                    "success": False,
                    "error_code": f"RAZORPAY_HTTP_{resp.status_code}",
                    "error_message": f"Razorpay API returned HTTP {resp.status_code}: {err_msg}"
                }
        except httpx.TimeoutException:
            logger.error(f"Razorpay API search request timed out for reference_id={reference_id}")
            return {
                "success": False,
                "error_code": "RAZORPAY_TIMEOUT",
                "error_message": "Connection to Razorpay Payment Links API timed out."
            }
        except Exception as e:
            logger.error(f"Failed to query Razorpay Payment Link by reference_id: {str(e)}")
            return {
                "success": False,
                "error_code": "RAZORPAY_CONNECTION_ERROR",
                "error_message": f"Failed to connect to Razorpay API: {str(e)}"
            }
