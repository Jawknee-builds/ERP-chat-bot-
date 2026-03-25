import asyncio
from pydantic_ai import Agent
from dotenv import load_dotenv

load_dotenv()

agent = Agent('gemini-2.5-flash')

async def main():
    try:
        r = await agent.run('hello')
        print("DIR:", dir(r))
        print("DATA_ATTR:", hasattr(r, 'data'), getattr(r, 'data', None))
    except Exception as e:
        print("Run Error:", repr(e))

if __name__ == "__main__":
    asyncio.run(main())
