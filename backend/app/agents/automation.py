from pydantic_ai import Agent, RunContext
from app.integrations.unified_client import UnifiedClient

# The Automation Action Agent
automation_agent = Agent(
    model='gemini-2.5-pro',
    system_prompt=(
        "You are an expert ERP Automation Agent with complete read and write access to all of the user's "
        "connected software systems (CRMs, Accounting ERPs, ATS, etc). "
        "When the user makes a request (like 'create a new HubSpot contact called John'), you are equipped "
        "with powerful tools to execute those changes on their behalf natively. "
        "Figure out the correct category (e.g. 'crm', 'accounting') and object type (e.g. 'contact', 'invoice') "
        "based on the tool's documentation and user intent, and execute the API call natively. "
        "Always respond with a clear summary of what you created or updated and any IDs returned."
    ),
    deps_type=UnifiedClient
)

@automation_agent.tool
async def create_record(ctx: RunContext[UnifiedClient], connection_id: str, category: str, object_type: str, payload: dict) -> str:
    """
    Creates a new native record in the connected ERP. 
    `category` should be strings like "crm" or "accounting".
    `object_type` should be strings like "contact", "company", "invoice".
    """
    try:
        result = await ctx.deps.create_object(connection_id, category, object_type, payload)
        return f"Success! Output: {result}"
    except Exception as e:
        return f"Error executing creation: {str(e)}"

@automation_agent.tool
async def update_record(ctx: RunContext[UnifiedClient], connection_id: str, category: str, object_type: str, object_id: str, payload: dict) -> str:
    """
    Updates an existing record in the ERP.
    `object_id` is the ID of the resource in the external system.
    """
    try:
        result = await ctx.deps.update_object(connection_id, category, object_type, object_id, payload)
        return f"Success! Output: {result}"
    except Exception as e:
        return f"Error executing update: {str(e)}"

@automation_agent.tool
async def run_passthrough_query(ctx: RunContext[UnifiedClient], connection_id: str, method: str, path: str, payload: dict = None) -> str:
    """
    Executes a raw 'passthrough' API query directly on the downstream integration. 
    Use this if the universal object methods cannot support a specific niche field logic.
    `method` is GET, POST, PATCH, etc. `path` is the relative URL natively.
    """
    try:
        result = await ctx.deps.passthrough_request(connection_id, method, path, payload)
        return f"Passthrough result: {result}"
    except Exception as e:
        return f"Error running passthrough: {str(e)}"
