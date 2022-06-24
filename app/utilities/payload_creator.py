from app.models.api import GenerateCashFreePaymentLinkRequest

def createCashFreeLinkGeneratorPayload(mobile: str,  unique_id: str,
    amount: int, purpose: str, expiry: str) -> GenerateCashFreePaymentLinkRequest:
    
    payload = GenerateCashFreePaymentLinkRequest(
        customer_details = {'customer_phone': mobile},
        link_id = unique_id,
        link_amount = amount,
        link_purpose = purpose,
        link_expiry_time = expiry,
    )
    return payload
