from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
import uuid

app = FastAPI()

class PaymentRequest(BaseModel):
    amount: float
    currency: str
    metadata: dict | None = None
    from_address: str | None = None
    network: str | None = None

@app.get("/list")
async def list_networks():
    return {"networks": ["base-sepolia", "base", "polygon-mumbai", "solana-devnet"]}

@app.post("/create_payment")
async def create_payment(req: PaymentRequest, response: Response):
    tx_id = "tx_" + uuid.uuid4().hex[:12]
    response.headers["X-PAYMENT-RESPONSE"] = tx_id
    return {"id": tx_id, "status": "success", "received": req.dict()}

@app.post("/verify")
async def verify(req: PaymentRequest):
    # simple echo verification
    return {"ok": True, "message": "verified", "received": req.dict()}

@app.post("/settle")
async def settle(req: PaymentRequest, response: Response):
    tx_id = "tx_" + uuid.uuid4().hex[:12]
    response.headers["X-PAYMENT-RESPONSE"] = tx_id
    return {"id": tx_id, "status": "settled", "received": req.dict()}

