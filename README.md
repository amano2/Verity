# 📰 Verity: AI-Powered News Verifier

**Verity** is a state-of-the-art multimodal news verification platform designed to combat misinformation in the digital age. It combines robust web scraping, factual claim extraction via advanced Large Language Models (LLMs), and real-time cross-referencing to provide a comprehensive "Truth Score" for any news article.

---

## ✨ Features

- **Automated Article Scraping**: Cleanly extracts headlines, authors, publish dates, and body text from any news URL, stripping away ads and boilerplate.
- **AI Claim Extraction**: Leverages **Llama 3.3 70B (via OpenRouter)** to identify the most critical, verifiable factual claims from long-form content.
- **Real-Time Cross-Referencing**: Performs live web searches using **DuckDuckGo** to find supporting evidence or contradicting reports.
- **Intelligent Truth Scoring**: Calculates a factual integrity score (0-100) based on cross-referenced evidence and provides detailed verdicts for each claim.
- **Premium Newspaper UI**: A bespoke, parchment-toned interface that evokes the gravitas of traditional journalism with modern, responsive features.
- **Built-in Resilience**: Implements strict rate-limiting (to respect free-tier API quotas) and robust retry logic via **Tenacity**.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **LLM**: Meta Llama 3.3 70B Instruct (via **OpenRouter**)
- **AI Orchestration**: OpenAI-compatible API integration
- **Search**: DuckDuckGo Search API (LangChain integration)
- **Scraping**: BeautifulSoup4
- **Resilience**: Tenacity (Retry logic) & Asyncio (Non-blocking operations)

### Frontend
- **Framework**: React.js with Vite
- **Styling**: Vanilla CSS (Premium Newspaper Theme)
- **Typography**: DM Serif Display & Lora (Google Fonts)
- **UX**: Dynamic multi-step progress indicators ("Printing Press" mode)

---

## 🚀 Getting Started

### Prerequisites
- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js & npm](https://nodejs.org/)
- [OpenRouter API Key](https://openrouter.ai/)

### 1. Backend Setup
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   Create a `.env` file in the `backend/` folder:
   ```env
   OPENROUTER_API_KEY="YOUR_OPENROUTER_KEY_HERE"
   OPENROUTER_MODEL="meta-llama/llama-3.3-70b-instruct:free"
   ```

### 2. Frontend Setup
1. Navigate to the `frontend/` directory:
   ```bash
   cd ../frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```

---

## 📖 How to Use (Step-by-Step)

1. **Launch the Backend**:
   From the `backend/` folder, run:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   *The API will be available at `http://localhost:8000`.*

2. **Launch the Frontend**:
   From the `frontend/` folder, run:
   ```bash
   npm run dev
   ```
   *Open the URL shown in your terminal (usually `http://localhost:5173`).*

3. **Verify an Article**:
   - Copy a news article URL (e.g., from BBC, Reuters, or CNN).
   - Paste it into the central search bar in Verity.
   - Click **"Analyze"**.
   - Watch the **"Printing Press"** status indicators as the AI scrapes, extracts, and verifies claims.

4. **Review Results**:
   - Check the **Integrity Assessment** score and reliability label.
   - Review each **Factual Evidence Card** to see the verdict, explanation, and confidence level.

---

## 🛡️ Stability & Limits
Verity is optimized for free-tier reliability:
- **Rate Limiting**: The system deliberately spaces claim verification calls (approx. 8 seconds apart) to respect OpenRouter's free-tier limits (8 req/min).
- **Concurrency**: Operations are asynchronous to ensure the UI remains responsive during long-running verification tasks.

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for more information.

---
*Built by [amano2](https://github.com/amano2).*

