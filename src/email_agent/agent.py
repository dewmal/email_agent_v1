from pydantic_ai import Agent

from dotenv import load_dotenv

load_dotenv()

agent = Agent("groq:openai/gpt-oss-120b")

if __name__ == "__main__":
    agent.run_sync("HI")