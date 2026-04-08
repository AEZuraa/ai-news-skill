---
name: ai-news
description: >-
  Собирает и фильтрует AI-новости из RSS-источников (ArXiv, TechCrunch,
  MIT Tech Review и др.). Вызывается командой /news, возвращает
  подборку свежих новостей по AI/ML прямо в контекст чата.
---

# ai-news

Скилл для сбора AI-новостей из RSS-фидов. Парсит несколько источников,
фильтрует по ключевым словам и возвращает результат в Markdown или JSON.

## Зависимости

```bash
pip install -r requirements.txt
```

## Использование в Claude Code

Скилл добавляет команду `/news`. Напишите в чате:

```
/news
```

С параметрами:

```
/news за последние 7 дней, покажи 10 штук
```

## Прямой запуск

```bash
python fetch_news.py                           # markdown, 3 дня, 20 новостей
python fetch_news.py --days 7 --limit 10       # настройка
python fetch_news.py --format json             # JSON
python fetch_news.py --all                     # без AI-фильтра
```

## Источники по умолчанию

- MIT Technology Review
- TechCrunch AI
- The Verge AI
- ArXiv cs.AI
- OpenAI News
- Google Blog
- Google Research Blog
- Google DeepMind Blog
- Hugging Face Blog
- WIRED AI
- AWS Machine Learning Blog
- Microsoft Research Blog
- Anthropic News
- NVIDIA Technical Blog
- MIT News AI

Можно подключить свои: `python fetch_news.py --sources my_sources.json`

Формат файла:

```json
[
  {"name": "My Source", "url": "https://example.com/rss", "tag": "custom"}
]
```

## Что внутри

- `fetch_news.py` — основной скрипт, парсит RSS через feedparser
- `.claude/commands/news.md` — определение slash-команды для Claude Code
- Фильтрация по ~50 ключевым словам (ai, llm, transformer, и т.д.)
- Вывод: Markdown (по умолчанию) или JSON
