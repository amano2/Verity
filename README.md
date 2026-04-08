# 📰 Verity: AI-Powered News Verifier

**Verity** is a state-of-the-art multimodal news verification platform designed to combat misinformation. It combines deep web scraping, factual claim extraction via Large Language Models (LLMs), and real-time cross-referencing to provide users with a "Truth Score" for any news article.

---

## ✨ Features

- **Automated Article Scraping**: Cleanly extracts content, headlines, and metadata from any news URL.
- **AI Claim Extraction**: Uses **Google Gemini 2.5 Flash** to identify 3-5 core, verifiable factual claims.
- **Real-Time Cross-Referencing**: Searches the live web using **DuckDuckGo** to find supporting or contradicting evidence.
- **Reliability Meter**: Calculates a factual integrity score and provides a detailed verdict (True, Mostly True, Misleading, False) for every claim.
- **Premium Newspaper UI**: A bespoke, parchment-toned interface designed for professional journalism.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **AI Orchestration**: Google GenAI SDK & LangChain
- **Search**: DuckDuckGo Search API
- **Scraping**: BeautifulSoup4
- **Resilience**: Tenacity (Retry logic for API stability)

### Frontend
- **Framework**: React.js with Vite
- **Styling**: Vanilla CSS (Newspaper Theme)
- **Typography**: DM Serif Display & Lora (Google Fonts)

---

## 🚀 Getting Started

### Prerequisites
- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js & npm](https://nodejs.org/)
- [Google Gemini API Key](https://aistudio.google.com/app/apikey)

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
   GOOGLE_API_KEY="YOUR_KEY_HERE"
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
   uvicorn main:app --reload
   ```
   *The API will be available at `http://localhost:8000`.*

2. **Launch the Frontend**:
   From the `frontend/` folder, run:
   ```bash
   npm run dev
   ```
   *Open `http://localhost:5173` in your browser.*

3. **Verify an Article**:
   - Copy a news article URL (e.g., from BBC, Reuters, or CNN).
   - Paste it into the central search bar in Verity.
   - Click **"Verify Article"**.
   - Wait for the "Printing Press" to finish analysis.

4. **Review Results**:
   - Scroll through the **Factual Integrity Score**.
   - Review each **Claim Card** to see the verdict, confidence level, and source links.

---

## 🛡️ Security & Privacy
Verity is designed with security in mind:
- **Environment Variables**: API keys are stored in excluded `.env` files.
- **Rate Limiting**: Integrated retry logic handles Gemini free-tier limits gracefully.

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for more information.

---
*Built with ❤️ by [amano2](https://github.com/amano2) & Antigravity.*
