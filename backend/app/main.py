from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

# Load env variables before importing AI models
load_dotenv()

from app.agents.discovery import router_agent, discovery_agent, analyst_agent
from app.agents.automation import automation_agent
from app.integrations.unified_client import UnifiedClient
from app.database import get_db_connection
from app.schemas.manifest import Customer, Product, Invoice

class InvoiceItem(BaseModel):
    id: int
    invoice_id: str
    product_id: str
    quantity: int
    unit_price: float

app = FastAPI(title="Erpy-Middleware")

# Configure CORS for the Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_message: str
    connection_id: str

def get_unified_client():
    return UnifiedClient()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/chat")
async def process_chat(request: ChatRequest, client: UnifiedClient = Depends(get_unified_client)):
    # 1. Route intent using Gemini 2.5 Flash
    try:
        routing_result = await router_agent.run(request.user_message)
        # Handle breaking changes in pydantic-ai API where .data became .output
        intent = getattr(routing_result, 'data', getattr(routing_result, 'output', '')).strip().upper()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing error: {str(e)}")

    if intent in ["ANALYTICS", "SUMMARY", "UNKNOWN"]:
        try:
            conn = get_db_connection()
            cust_rows = conn.execute("SELECT * FROM customers").fetchall()
            prod_rows = conn.execute("SELECT * FROM products").fetchall()
            inv_rows = conn.execute("SELECT * FROM invoices").fetchall()
            line_rows = conn.execute("SELECT * FROM invoice_items").fetchall()
            conn.close()
            
            context = (
                f"Customers (JSON): {[dict(r) for r in cust_rows]}\n"
                f"Products (JSON): {[dict(r) for r in prod_rows]}\n"
                f"Invoices (JSON): {[dict(r) for r in inv_rows]}\n"
                f"Invoice Line Items (who bought what): {[dict(r) for r in line_rows]}"
            )
            # Pass the ACTUAL user message so the agent can answer specific questions!
            analyst_result = await analyst_agent.run(f"User Question: '{request.user_message}'\n\nDatabase Context:\n{context}")
            final_data = getattr(analyst_result, 'data', getattr(analyst_result, 'output', ''))
            return {"intent": "ANALYTICS", "result": final_data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

    # 3. If intent requires discovery, run the Discovery Agent (Gemini 2.5 Pro)
    if intent == "DISCOVERY":
        try:
            discovery_result = await discovery_agent.run(
                f"Analyze connection {request.connection_id} based on intent: {intent}",
                deps=client
            )
            final_data = getattr(discovery_result, 'data', getattr(discovery_result, 'output', ''))
            return {"intent": intent, "result": final_data}
        except Exception as e:
             raise HTTPException(status_code=500, detail=f"Discovery error: {str(e)}")

    # 4. If intent is automation, run the Automation Action Agent (Gemini 2.5 Pro)
    if intent in ["AUTOMATION", "ACTION", "UPDATE"]:
        try:
            # We provide the user's message natively and pass the unified client dep
            automation_result = await automation_agent.run(
                f"Connection ID: {request.connection_id}\nInstruction: {request.user_message}",
                deps=client
            )
            final_data = getattr(automation_result, 'data', getattr(automation_result, 'output', ''))
            return {"intent": intent, "result": final_data}
        except Exception as e:
             raise HTTPException(status_code=500, detail=f"Automation error: {str(e)}")

    return {"intent": intent, "message": "Intent recognized but no specific action logic implemented for this intent yet."}

# DUMMY DATABASE ENDPOINTS FOR UI INTERACTION
@app.get("/api/customers", response_model=List[Customer])
def get_customers():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM customers").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/products", response_model=List[Product])
def get_products():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/invoices", response_model=List[Invoice])
def get_invoices():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM invoices").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/invoice_items", response_model=List[InvoiceItem])
def get_invoice_items():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM invoice_items").fetchall()
    conn.close()
    return [dict(row) for row in rows]
