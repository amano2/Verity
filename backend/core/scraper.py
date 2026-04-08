import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

class ArticleScraper:
    @staticmethod
    def scrape(url: str) -> Dict[str, Any]:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Basic article extraction logic
            # Extract headline
            title = ""
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text().strip()
            elif soup.title:
                title = soup.title.get_text().strip()
                
            # Extract main body text
            # Often news articles are in <article> or specific classes
            body_text = ""
            article_tag = soup.find("article")
            if article_tag:
                # Remove script and style elements
                for s in article_tag(["script", "style", "nav", "footer", "header", "aside"]):
                    s.decompose()
                body_text = article_tag.get_text(separator="\n").strip()
            else:
                # Fallback: get all paragraph text
                paragraphs = soup.find_all("p")
                body_text = "\n".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20])
            
            # Basic metadata extraction
            author = None
            author_tag = soup.find("meta", attrs={"name": "author"}) or soup.find("a", attrs={"rel": "author"})
            if author_tag:
                author = author_tag.get("content") or author_tag.get_text()
                
            publish_date = None
            date_tag = soup.find("meta", attrs={"property": "article:published_time"}) or soup.find("time")
            if date_tag:
                publish_date = date_tag.get("content") or date_tag.get("datetime") or date_tag.get_text()
                
            return {
                "title": title,
                "body": body_text,
                "author": author,
                "publish_date": publish_date,
                "url": url
            }
        except Exception as e:
            raise Exception(f"Failed to scrape URL: {str(e)}")
