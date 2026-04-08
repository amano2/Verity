from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class VerifyRequest(BaseModel):
    url: HttpUrl

class Source(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None

class ClaimAnalysis(BaseModel):
    claim: str
    verdict: str  # True, False, Mostly True, Misleading, Unverified
    confidence_score: int  # 0-100
    explanation: str
    sources: List[Source]

class ArticleMetadata(BaseModel):
    title: str
    author: Optional[str] = None
    publish_date: Optional[str] = None
    summary: Optional[str] = None

class VerifyResponse(BaseModel):
    metadata: ArticleMetadata
    factual_integrity_score: int
    reliability_label: str
    claims: List[ClaimAnalysis]
    status: str = "success"
