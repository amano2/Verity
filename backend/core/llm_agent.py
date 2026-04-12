import os
import json
import logging
import asyncio
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from tenacity import retry, stop_after_attempt, wait_fixed

load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Free tier = 8 req/min → space calls at least 8s apart
REQUEST_DELAY = 8.0


class NewsVerifierAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
        self.model_name = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
        self.search = DuckDuckGoSearchRun()
        logger.info(f"NewsVerifierAgent initialized with model: {self.model_name}")

    def _safe_parse_json(self, text: str) -> Any:
        """Safely parses JSON from LLM output, handling markdown blocks."""
        try:
            clean_text = text.strip()
            if clean_text.startswith("```"):
                lines = clean_text.split("\n")
                clean_text = "\n".join(lines[1:-1])
            data = json.loads(clean_text)
            if isinstance(data, list) and len(data) > 0:
                return data[0] if isinstance(data[0], dict) else data
            return data
        except Exception as e:
            logger.error(f"Failed to parse JSON: {text[:200]}. Error: {e}")
            raise

    def _call_llm(self, prompt: str) -> str:
        """Call OpenRouter via the OpenAI-compatible API."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional fact-checker. Always respond with valid JSON only, no extra commentary."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_fixed(15),
        reraise=True,
        before_sleep=lambda rs: logger.info(f"Rate limited. Waiting 15s (attempt {rs.attempt_number})...")
    )
    async def extract_claims(self, article_text: str) -> List[str]:
        prompt = (
            "Act as a rigorous fact-checker. Extract exactly 3 core, verifiable factual claims "
            "from the following news article. "
            "Focus on specific statements about events, dates, numbers, or people. "
            "Return ONLY a valid JSON array of 3 strings. Example: [\"claim1\", \"claim2\", \"claim3\"]\n\n"
            f"Article Text:\n{article_text[:8000]}\n\n"
            "JSON Array:"
        )
        loop = asyncio.get_event_loop()
        response_text = await loop.run_in_executor(None, self._call_llm, prompt)
        data = self._safe_parse_json(response_text)
        if isinstance(data, list):
            return data[:3]
        elif isinstance(data, dict) and "claims" in data:
            return data["claims"][:3]
        return [str(data)] if data else []

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_fixed(15),
        reraise=True,
        before_sleep=lambda rs: logger.info(f"Rate limited. Waiting 15s (attempt {rs.attempt_number})...")
    )
    async def verify_claim(self, claim: str, original_context: str) -> Dict[str, Any]:
        try:
            search_results = self.search.run(claim)
        except Exception:
            search_results = "No search results found."

        prompt = (
            "You are a professional fact-checker. Verify the following claim using the provided search results "
            "and original article context.\n\n"
            f"Claim: {claim}\n"
            f"Original Context Snippet: {original_context[:500]}\n"
            f"Search Results: {search_results[:1000]}\n\n"
            "Output ONLY a valid JSON object with these exact keys:\n"
            "- claim: The original claim string\n"
            "- verdict: One of (True, False, Mostly True, Misleading, Unverified)\n"
            "- confidence_score: An integer from 0 to 100\n"
            "- explanation: A brief explanation (2-3 sentences)\n"
            "- sources: A list of objects with 'url' and 'title' keys\n\n"
            "JSON Output:"
        )
        loop = asyncio.get_event_loop()
        response_text = await loop.run_in_executor(None, self._call_llm, prompt)
        return self._safe_parse_json(response_text)

    async def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Extract claims
        try:
            claims_list = await self.extract_claims(article["body"])
            logger.info(f"Extracted {len(claims_list)} claims.")
        except Exception as e:
            logger.error(f"Claim extraction failed: {e}")
            return {
                "metadata": {
                    "title": article["title"],
                    "author": article.get("author"),
                    "publish_date": article.get("publish_date"),
                    "summary": article["body"][:200] + "..."
                },
                "factual_integrity_score": 0,
                "reliability_label": "Could Not Verify",
                "claims": [{
                    "claim": "Analysis failed.",
                    "verdict": "Unverified",
                    "confidence_score": 0,
                    "explanation": "API rate limit exceeded. Please wait ~1 minute and try again.",
                    "sources": []
                }]
            }

        # 2. Verify each claim — space calls to respect 8 req/min limit
        verified_claims = []
        total_score = 0

        for i, claim in enumerate(claims_list):
            if i > 0:
                logger.info(f"Waiting {REQUEST_DELAY}s before next claim (rate limit)...")
                await asyncio.sleep(REQUEST_DELAY)

            try:
                result = await self.verify_claim(claim, article["body"])
                if isinstance(result, list) and len(result) > 0:
                    result = result[0]
            except Exception as e:
                logger.warning(f"Failed to verify claim: {e}")
                result = {
                    "claim": claim,
                    "verdict": "Unverified",
                    "confidence_score": 0,
                    "explanation": "Could not verify — API rate limit reached.",
                    "sources": []
                }

            verified_claims.append(result)
            verdict_scores = {"True": 100, "Mostly True": 75, "Unverified": 50, "Misleading": 25, "False": 0}
            verdict = str(result.get("verdict", "Unverified")).title()
            total_score += verdict_scores.get(verdict, 50)

        avg_score = int(total_score / len(verified_claims)) if verified_claims else 0
        label = "High Reliability" if avg_score >= 80 else "Mixed Reliability" if avg_score >= 60 else "Low Reliability / Caution"

        return {
            "metadata": {
                "title": article["title"],
                "author": article.get("author"),
                "publish_date": article.get("publish_date"),
                "summary": article["body"][:200] + "..."
            },
            "factual_integrity_score": avg_score,
            "reliability_label": label,
            "claims": verified_claims
        }
