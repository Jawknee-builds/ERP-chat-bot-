from pydantic_ai import Agent, RunContext
from app.schemas.manifest import Customer, Invoice, Product
from app.integrations.unified_client import UnifiedClient
from dotenv import load_dotenv

load_dotenv()

# Use Gemini 2.5 Pro for complex discovery mapping
gemini_pro = 'gemini-2.5-pro'
# Use Gemini 2.5 Flash for fast intent routing
gemini_flash = 'gemini-2.5-flash'

# The Discovery Skill Agent
discovery_agent = Agent(
    model=gemini_pro,
    system_prompt=(
        "You are an ERP Discovery Expert. Your job is to analyze the metadata provided by "
        "the Unified.to API for a given ERP system, and map its custom fields to our "
        "standard JSON schemas (Customer, Invoice, Product). "
        "Use the analyze_erp_metadata tool to fetch the raw data and then explain the mapping."
    ),
    deps_type=UnifiedClient
)

@discovery_agent.tool
async def analyze_erp_metadata(ctx: RunContext[UnifiedClient], connection_id: str) -> str:
    """Fetches ERP metadata using the UnifiedClient and determines mapping strategy."""
    try:
        metadata = await ctx.deps.get_erp_metadata(connection_id)
        return f"Discovered metadata: {metadata}"
    except Exception as e:
        return f"Error fetching metadata: {str(e)}"

# The Analyst Agent
analyst_agent = Agent(
    model=gemini_flash,
    system_prompt=(
        "You are an expert Business Analyst talking directly to a business owner over chat. "
        "You will be provided with raw JSON data of their Customers, Products, Invoices, and Line Items. "
        "Answer their question accurately using the provided data context. "
        "IMPORTANT: If they ask for a general summary, give a friendly 3-sentence summary of the business. "
        "If they ask about a SPECIFIC product, customer, or invoice, ONLY discuss that specific item in detail. "
        "Speak naturally and directly to them. Do not hallucinate data that isn't provided."
    )
)

# The Intent Routing Agent
router_agent = Agent(
    model=gemini_flash,
    system_prompt=(
        "You are a high-speed intent router. Analyze the user's request related to "
        "ERP integration and route it to the appropriate sub-agent action. "
        "Must return one of these strictly: ['DISCOVERY', 'SYNC', 'TRANSFORM', 'ANALYTICS', 'AUTOMATION', 'UNKNOWN']"
    )
)
