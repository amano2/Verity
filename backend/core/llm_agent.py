import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Union
from google import genai
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from tenacity import retry, stop_after_attempt, wait_random_exponential

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsVerifierAgent:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        # Using a stable Gemini 2.5 model variant
        self.model_name = "gemini-2.5-flash"
        self.search = DuckDuckGoSearchRun()

    def _safe_parse_json(self, text: str) -> Any:
        """Safely parses JSON from LLM output, handling markdown blocks and lists."""
        try:
            # Clean text from potential markdown backticks
            clean_text = text.strip()
            if clean_text.startswith("```"):
                # Extract content from markdown block
                lines = clean_text.split("\n")
                if lines[0].startswith("```json"):
                    clean_text = "\n".join(lines[1:-1])
                else:
                    clean_text = "\n".join(lines[1:-1])
            
            data = json.loads(clean_text)
            
            # If the model returned a list (likely index 0), extract it
            if isinstance(data, list) and len(data) > 0:
                return data[0] if isinstance(data[0], dict) else data
            return data
        except Exception as e:
            logger.error(f"Failed to parse JSON output: {text}. Error: {e}")
            raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_random_exponential(multiplier=1, min=4, max=30),
        reraise=True,
        before_sleep=lambda retry_state: logger.info(f"Retrying claim extraction (attempt {retry_state.attempt_number})...")
    )
    async def extract_claims(self, article_text: str) -> List[str]:
        prompt = (
            "Act as a rigorous fact-checker. Extract 3 to 5 core, verifiable factual claims from the following news article text. "
            "Focus on specific statements about events, dates, numbers, or people that can be cross-referenced. "
            "Return the claims ONLY in a JSON array of strings.\n\n"
            f"Article Text: {article_text[:10000]}\n\n"
            "JSON Array:"
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        data = self._safe_parse_json(response.text)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "claims" in data:
            return data["claims"]
        return [str(data)] if data else []

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_random_exponential(multiplier=1, min=4, max=30),
        reraise=True,
        before_sleep=lambda retry_state: logger.info(f"Retrying claim verification (attempt {retry_state.attempt_number})...")
    )
    async def verify_claim(self, claim: str, original_context: str) -> Dict[str, Any]:
        try:
            # Add some jitter/sleep to avoid hitting DuckDuckGo rate limits too hard
            await asyncio.sleep(1)
            search_results = self.search.run(claim)
        except Exception:
            search_results = "No search results found."

        prompt = (
            "You are a professional fact-checker. Verify the following claim using the provided search results and original context.\n\n"
            f"Claim: {claim}\n"
            f"Original Context Snippet: {original_context[:500]}\n"
            f"Search Results: {search_results}\n\n"
            "Output precisely a JSON object with the following keys:\n"
            "- claim: The original claim string\n"
            "- verdict: One of (True, False, Mostly True, Misleading, Unverified)\n"
            "- confidence_score: An integer from 0 to 100\n"
            "- explanation: A brief explanation of the verdict (2-3 sentences)\n"
            "- sources: A list of objects with 'url' and 'title' keys (extract from search results if possible)\n\n"
            "JSON Output:"
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        return self._safe_parse_json(response.text)

    async def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Extract claims with failure fallback
        try:
            claims_list = await self.extract_claims(article["body"])
        except Exception as e:
            logger.error(f"Critical failure in claim extraction: {e}")
            claims_list = ["Verification skipped due to API demand."]

        # 2. Verify each claim with per-claim resilience
        verified_claims = []
        total_score = 0
        
        for claim in claims_list:
            try:
                result = await self.verify_claim(claim, article["body"])
                # Handle case where result might be a list despite safe_parse (extra safety)
                if isinstance(result, list) and len(result) > 0:
                    result = result[0]
            except Exception as e:
                logger.warning(f"Failed to verify claim '{claim}': {e}")
                result = {
                    "claim": claim,
                    "verdict": "Unverified",
                    "confidence_score": 0,
                    "explanation": "Fact-checking system reached capacity limit for this specific claim. Please try again later.",
                    "sources": []
                }
            
            verified_claims.append(result)
            
            verdict_scores = {
                "True": 100,
                "Mostly True": 75,
                "Unverified": 50,
                "Misleading": 25,
                "False": 0
            }
            # Robust verdict lookup in case of small LLM hallucinations in casing
            verdict = str(result.get("verdict", "Unverified")).title()
            total_score += verdict_scores.get(verdict, 50)
            
        avg_score = int(total_score / len(verified_claims)) if verified_claims else 0
        
        if avg_score >= 80:
            label = "High Reliability"
        elif avg_score >= 60:
            label = "Mixed Reliability"
        else:
            label = "Low Reliability/Caution"
            
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
