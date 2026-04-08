import asyncio
import json
import os
from core.scraper import ArticleScraper
from core.llm_agent import NewsVerifierAgent
from dotenv import load_dotenv

load_dotenv()

async def test():
    try:
        scraper = ArticleScraper()
        agent = NewsVerifierAgent()
        url = "https://www.bbc.com/news/world-60525350"
        print(f"Scraping {url}...")
        article = scraper.scrape(url)
        print(f"Analyzing claims...")
        result = await agent.analyze_article(article)
        print("\n=== VERIFICATION RESULT ===")
        print(json.dumps(result, indent=2))
        print("===========================")
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(test())
