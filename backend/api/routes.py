from fastapi import APIRouter, HTTPException
from models.schemas import VerifyRequest, VerifyResponse
from core.scraper import ArticleScraper
from core.llm_agent import NewsVerifierAgent

router = APIRouter()
agent = NewsVerifierAgent()

@router.post("/verify", response_model=VerifyResponse)
async def verify_article(request: VerifyRequest):
    try:
        # 1. Scrape
        article_data = ArticleScraper.scrape(str(request.url))
        
        # 2. Analyze
        analysis_result = await agent.analyze_article(article_data)
        
        return VerifyResponse(**analysis_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
