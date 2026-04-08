"""
Fetch and parse AI-related news from RSS feeds.

Usage: python fetch_news.py [--days N] [--limit N] [--format markdown|json]
"""

import sys
import re
import json
import html
import argparse
from datetime import datetime, timedelta

try:
    import feedparser
except ImportError:
    sys.exit("feedparser is not installed. Run: pip install feedparser")

try:
    import requests
except ImportError:
    sys.exit("requests is not installed. Run: pip install requests")


RSS_SOURCES = [
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "tag": "tech"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "tag": "industry"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "tag": "industry"},
    {"name": "OpenAI News", "url": "https://openai.com/news/rss.xml", "tag": "company"},
    {"name": "Google Blog", "url": "https://blog.google/rss", "tag": "company"},
    {"name": "Google Research Blog", "url": "https://research.google/blog/rss", "tag": "research"},
    {"name": "Google DeepMind Blog", "url": "https://deepmind.google/discover/blog/rss.xml", "tag": "research"},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml", "tag": "tools"},
    {"name": "WIRED AI", "url": "https://www.wired.com/feed/category/ai/latest/rss", "tag": "industry"},
    {"name": "AWS Machine Learning Blog", "url": "https://aws.amazon.com/blogs/machine-learning/feed/", "tag": "company"},
    {"name": "Microsoft Research Blog", "url": "https://www.microsoft.com/en-us/research/feed/", "tag": "research"},
    {"name": "Anthropic News", "url": "https://www.anthropic.com/news/rss.xml", "tag": "company"},
    {"name": "NVIDIA Technical Blog", "url": "https://developer.nvidia.com/blog/category/deep-learning/feed/", "tag": "tools"},
    {"name": "MIT News AI", "url": "https://news.mit.edu/topic/artificial-intelligence2/rss.xml", "tag": "research"},
    {"name": "ArXiv cs.AI", "url": "https://rss.arxiv.org/rss/cs.AI", "tag": "research"},  # очень много research статей в день, все результаты поиска занимают
]


AI_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "neural network", "llm", "large language model", "gpt", "claude",
    "transformer", "generative", "generative ai", "gen ai", "openai", "anthropic", "deepmind",
    "diffusion", "nlp", "computer vision", "robotics", "reasoning",
    "agi", "foundation model", "world model", "multimodal", "vision-language model", "vlm",
    "agent", "agents", "ai agent", "tool use", "mcp",
    "fine-tuning", "fine tuning", "pretraining", "model training", "inference",
    "rag", "retrieval", "semantic search", "embeddings", "embedding", "vector database", "rerank",
    "prompt", "prompting", "context window", "context length",
    "alignment", "safety", "eval", "benchmark",
    "speech", "audio", "voice", "text-to-speech", "tts", "asr",
]



def fetch_feed(url, timeout = 15):
    """Download and parse an RSS feed."""
    try:
        resp = requests.get(url, timeout = timeout, headers = {
            "User-Agent": "ai-news-skill/1.0"
        })
        feed = feedparser.parse(resp.content)
        return feed.entries
    except Exception as e:
        print(f"  [!] {url}: {e}", file = sys.stderr)
        return []


def extract_date(entry):
    """Try to read publication date from a feed entry."""
    for field in ("published_parsed", "updated_parsed"):
        val = getattr(entry, field, None)
        if val:
            try:
                return datetime(*val[:6])
            except (TypeError, ValueError):
                pass
    return None


def strip_html(text):
    """Strip HTML tags and decode entities from text."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def matches_ai(title, summary = ""):
    """Return True if title/summary matches AI-related keywords."""
    text = f"{title} {summary}".lower()
    return any(kw in text for kw in AI_KEYWORDS)


def collect_news(sources, days = 3, limit = 30, ai_only = True):
    """Walk sources, filter by date/keywords, sort and truncate."""
    cutoff = datetime.now() - timedelta(days = days)
    items = []

    for src in sources:
        print(f"  => {src['name']}...", file = sys.stderr)
        entries = fetch_feed(src["url"])

        for entry in entries:
            title = entry.get("title", "").strip()
            if not title:
                continue

            link = entry.get("link", "")
            raw_summary = entry.get("summary", "")
            summary = strip_html(raw_summary)[:300]
            pub_date = extract_date(entry)

            if pub_date and pub_date < cutoff:
                continue

            if ai_only and not matches_ai(title, summary):
                continue

            items.append({
                "title": title,
                "link": link,
                "source": src["name"],
                "tag": src.get("tag", ""),
                "date": pub_date.strftime("%Y-%m-%d") if pub_date else "n/a",
                "summary": summary,
            })

    items.sort(key = lambda x: x["date"], reverse=True)
    return items[:limit]


def to_markdown(items):
    """Format items as Markdown."""
    if not items:
        return "Новостей по AI не найдено за указанный период."

    lines = []
    lines.append(f"# AI-новости — {datetime.now().strftime('%d.%m.%Y')}")
    lines.append(f"Найдено: **{len(items)}**\n")

    cur_date = None
    for item in items:
        if item["date"] != cur_date:
            cur_date = item["date"]
            lines.append(f"\n## {cur_date}\n")

        tag = f" `{item['tag']}`" if item["tag"] else ""
        lines.append(f"- **[{item['title']}]({item['link']})**{tag} — _{item['source']}_")

        if item["summary"]:
            short = item["summary"][:200]
            if len(item["summary"]) > 200:
                short += "…"
            lines.append(f"  > {short}")
        lines.append("")

    return "\n".join(lines)


def to_json(items):
    """Serialize items to JSON."""
    return json.dumps(items, indent = 2, ensure_ascii = False)


def main():
    p = argparse.ArgumentParser(description = "Collect AI news from RSS feeds")
    p.add_argument("--days", type = int, default = 3,
                   help = "How many days back to include (default: 3)")
    p.add_argument("--limit", type = int, default = 20,
                   help = "Max number of items (default: 20)")
    p.add_argument("--format", choices = ["markdown", "json"], default = "markdown",
                   help = "Output format (default: markdown)")
    p.add_argument("--all", action = "store_true",
                   help = "Show all items, skip AI keyword filter")
    p.add_argument("--sources", type = str, default = None,
                   help = "Path to JSON file with custom feed sources")
    args = p.parse_args()

    sources = RSS_SOURCES
    if args.sources:
        with open(args.sources) as f:
            sources = json.load(f)

    print("Собираю новости...\n", file = sys.stderr)
    items = collect_news(sources, days = args.days, limit = args.limit,
                         ai_only = not args.all)
    print(f"\nГотово, найдено {len(items)} записей.\n", file = sys.stderr)

    if args.format == "json":
        print(to_json(items))
    else:
        print(to_markdown(items))


if __name__ == "__main__":
    main()
