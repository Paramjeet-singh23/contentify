from fastapi import FastAPI, HTTPException, Depends, Body, APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse
import stripe
from core.config import STRIPE_SECRET_KEY 
router = APIRouter()

# Set your secret key. Remember to switch to your live secret key in production!
# See your keys here: https://dashboard.stripe.com/account/apikeys
stripe.api_key = STRIPE_SECRET_KEY

class PaymentData(BaseModel):
    token: str

@router.post("/charge/")
async def create_charge(payment_data: PaymentData):
    try:
        # Use Stripe's library to make charges
        charge = stripe.Charge.create(
            amount=2000, # Amount in cents, for example: $20.00
            currency="usd",
            source=payment_data.token,
            description="My Payment"
        )
        return JSONResponse(content={"status": "success"}, status_code=200)
    except stripe.error.StripeError as e:
        # Handle the exception
        return JSONResponse(content={"status": "error", "error": str(e)}, status_code=400)
