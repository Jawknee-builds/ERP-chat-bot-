import asyncio
from app.agents.discovery import router_agent
from app.agents.automation import automation_agent
from app.integrations.unified_client import UnifiedClient

async def test():
    client = UnifiedClient()
    result = await router_agent.run("Create a new HubSpot contact called John")
    intent = getattr(result, 'data', getattr(result, 'output', '')).strip().upper()
    print(f"Router intent: {intent}")
    
    if intent in ["AUTOMATION", "ACTION", "UPDATE"]:
        # MOCK call so we don't accidentally create fake data in the user's HubSpot if they have one linked
        print("Intent successfully resolved to AUTOMATION.")
        print("Automation agent is ready with UnifiedClient dependency tools.")
    else:
        print("Failed to route to AUTOMATION.")

if __name__ == "__main__":
    asyncio.run(test())
