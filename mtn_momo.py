import requests
import uuid

# --------------------------
# Custom Error
# --------------------------
class MomoAPIError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# --------------------------
# MTN MoMo Disbursements SDK
# --------------------------
class MTNMomoDisbursements:
    def __init__(self, api_user, api_key, subscription_key, base_url="https://sandbox.momodeveloper.mtn.com"):
        self.api_user = api_user
        self.api_key = api_key
        self.subscription_key = subscription_key
        self.base_url = base_url
        self.token = None

    # --------------------------
    # Authentication
    # --------------------------
    def authenticate(self):
        """Fetch OAuth2 access token"""
        url = f"{self.base_url}/disbursement/token/"
        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
        }
        response = requests.post(url, headers=headers, auth=(self.api_user, self.api_key))
        self._handle_error(response)
        self.token = response.json()["access_token"]
        return self.token

    # --------------------------
    # Utilities
    # --------------------------
    def _auth_headers(self, reference_id=None, environment="sandbox"):
        if not self.token:
            self.authenticate()
        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-Target-Environment": environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json"
        }
        if reference_id:
            headers["X-Reference-Id"] = reference_id
        return headers

    def _handle_error(self, response):
        if response.status_code in [200, 201, 202]:
            try:
                return response.json() if response.text else {}
            except ValueError:
                return {}
        else:
            try:
                error = response.json()
            except ValueError:
                error = {"code": "UNKNOWN_ERROR", "message": response.text}
            raise MomoAPIError(error.get("code", "UNKNOWN_ERROR"),
                               error.get("message", "No error message provided"))

    # --------------------------
    # Account Validation
    # --------------------------
    def validate_account_holder(self, account_holder_id, account_holder_id_type="MSISDN", environment="sandbox"):
        url = f"{self.base_url}/disbursement/v1_0/accountholder/{account_holder_id_type}/{account_holder_id}/active"
        response = requests.get(url, headers=self._auth_headers(environment=environment))
        return self._handle_error(response)

    # --------------------------
    # Deposits
    # --------------------------
    def deposit(self, amount, currency, external_id, payee_party_id, payee_party_id_type="MSISDN",
                payer_message="", payee_note="", version="v1_0", environment="sandbox"):
        reference_id = str(uuid.uuid4())
        url = f"{self.base_url}/disbursement/{version}/deposit"
        body = {
            "amount": str(amount),
            "currency": currency,
            "externalId": external_id,
            "payee": {
                "partyIdType": payee_party_id_type,
                "partyId": payee_party_id
            },
            "payerMessage": payer_message,
            "payeeNote": payee_note
        }
        response = requests.post(url, headers=self._auth_headers(reference_id, environment), json=body)
        self._handle_error(response)
        return {"status": "PENDING", "reference_id": reference_id}

    def get_deposit_status(self, reference_id, environment="sandbox"):
        url = f"{self.base_url}/disbursement/v1_0/deposit/{reference_id}"
        response = requests.get(url, headers=self._auth_headers(environment=environment))
        return self._handle_error(response)

    # --------------------------
    # Refunds
    # --------------------------
    def refund(self, amount, currency, external_id, reference_id_to_refund,
               payer_message="", payee_note="", version="v1_0", environment="sandbox"):
        reference_id = str(uuid.uuid4())
        url = f"{self.base_url}/disbursement/{version}/refund"
        body = {
            "amount": str(amount),
            "currency": currency,
            "externalId": external_id,
            "payerMessage": payer_message,
            "payeeNote": payee_note,
            "referenceIdToRefund": reference_id_to_refund
        }
        response = requests.post(url, headers=self._auth_headers(reference_id, environment), json=body)
        self._handle_error(response)
        return {"status": "PENDING", "reference_id": reference_id}

    def get_refund_status(self, reference_id, environment="sandbox"):
        url = f"{self.base_url}/disbursement/v1_0/refund/{reference_id}"
        response = requests.get(url, headers=self._auth_headers(environment=environment))
        return self._handle_error(response)

    # --------------------------
    # Transfers
    # --------------------------
    def transfer(self, amount, currency, external_id, payee_party_id, payee_party_id_type="MSISDN",
                 payer_message="", payee_note="", environment="sandbox"):
        reference_id = str(uuid.uuid4())
        url = f"{self.base_url}/disbursement/v1_0/transfer"
        body = {
            "amount": str(amount),
            "currency": currency,
            "externalId": external_id,
            "payee": {
                "partyIdType": payee_party_id_type,
                "partyId": payee_party_id
            },
            "payerMessage": payer_message,
            "payeeNote": payee_note
        }
        response = requests.post(url, headers=self._auth_headers(reference_id, environment), json=body)
        self._handle_error(response)
        return {"status": "PENDING", "reference_id": reference_id}

    def get_transfer_status(self, reference_id, environment="sandbox"):
        url = f"{self.base_url}/disbursement/v1_0/transfer/{reference_id}"
        response = requests.get(url, headers=self._auth_headers(environment=environment))
        return self._handle_error(response)

    # --------------------------
    # Balance
    # --------------------------
    def get_balance(self, environment="sandbox"):
        url = f"{self.base_url}/disbursement/v1_0/account/balance"
        response = requests.get(url, headers=self._auth_headers(environment=environment))
        return self._handle_error(response)

    def get_balance_in_currency(self, currency, environment="sandbox"):
        url = f"{self.base_url}/disbursement/v1_0/account/balance/{currency}"
        response = requests.get(url, headers=self._auth_headers(environment=environment))
        return self._handle_error(response)

    # --------------------------
    # User Info
    # --------------------------
    def get_basic_user_info(self, account_holder_id, account_holder_id_type="MSISDN", environment="sandbox"):
        url = f"{self.base_url}/disbursement/v1_0/accountholder/{account_holder_id_type}/{account_holder_id}/basicuserinfo"
        response = requests.get(url, headers=self._auth_headers(environment=environment))
        return self._handle_error(response)

    def get_user_info_with_consent(self, environment="sandbox"):
        url = f"{self.base_url}/disbursement/oauth2/v1_0/userinfo"
        response = requests.get(url, headers=self._auth_headers(environment=environment))
        return self._handle_error(response)


# --------------------------
# Example Usage
# --------------------------
if __name__ == "__main__":
    momo = MTNMomoDisbursements(
        api_user="YOUR_API_USER",
        api_key="YOUR_API_KEY",
        subscription_key="YOUR_SUBSCRIPTION_KEY"
    )

    try:
        # Validate if account exists
        active = momo.validate_account_holder("231887716973")
        print("✅ Account active:", active)

        # Make a transfer
        result = momo.transfer(
            amount="5000",
            currency="UGX",
            external_id="TXN-001",
            payee_party_id="256772123456",
            payer_message="Salary",
            payee_note="October payout"
        )
        print("✅ Transfer result:", result)

    except MomoAPIError as e:
        print(f"❌ MoMo API Error: {e.code} - {e.message}")
