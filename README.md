# ai-news-skill

Скилл для Claude Code, который парсит AI-новости из RSS и показывает их в чате.

## Для кого и зачем

Скилл предназначен для разработчиков и AI‑инженеров, которые работают в Claude Code или OpenCode и хотят следить за новостями индустрии, не покидая терминал. Он собирает RSS‑ленты MIT Technology Review, TechCrunch, ArXiv и других источников, фильтрует их по тематике искусственного интеллекта и возвращает сжатый дайджест. Это экономит время, заменяя ручной обход нескольких сайтов и вкладок в браузере одной командой /news. Благодаря автоматической фильтрации вы не пропустите важные обновления моделей, научные статьи и анонсы крупных компаний. Инструмент особенно актуален в быстро меняющемся AI‑ландшафте, когда актуальная информация должна быть под рукой в любой момент.

## Установка

```bash
git clone <repo-url>
cd ai-news-skill

python3 -m venv .venv   # macOS / Linux
# python -m venv .venv  # Windows

source .venv/bin/activate              # macOS / Linux
# .venv\Scripts\activate.bat            # Windows (cmd)
# .\.venv\Scripts\Activate.ps1        # Windows (PowerShell)

pip install -r requirements.txt
```

### Подключение к Claude Code

Скопируйте `.claude/` и скрипт в корень вашего проекта:

```bash
cp -r .claude/ /path/to/your/project/.claude/
cp fetch_news.py /path/to/your/project/
cp requirements.txt /path/to/your/project/
```

Или просто клонируйте репозиторий в рабочую директорию — тогда всё подхватится автоматически.

После этого в Claude Code станет доступна команда `/news`.

### OpenCode

Для OpenCode принцип тот же — положите `news.md` в директорию пользовательских команд (формат может отличаться, см. документацию OpenCode). Скрипт `fetch_news.py` работает полностью автономно и не привязан к конкретному агенту.

## Использование

В Claude Code:

```
/news
/news за 7 дней, покажи 10 штук
```

Из терминала напрямую:

```bash
python fetch_news.py                      # дефолт: 3 дня, 20 новостей, markdown
python fetch_news.py --days 7 --limit 10  # за неделю, максимум 10
python fetch_news.py --format json        # вывод в JSON
python fetch_news.py --all                # без фильтрации по AI
```

### Свои источники

Создайте JSON-файл:

```json
[
  {"name": "My Blog", "url": "https://example.com/feed.xml", "tag": "custom"},
  {"name": "Reddit ML", "url": "https://www.reddit.com/r/MachineLearning/.rss", "tag": "community"}
]
```

И передайте его:

```bash
python fetch_news.py --sources my_sources.json
```

## Что можно улучшить

1. **Больше источников и ключевых слов** — сейчас подключено 15 RSS-фидов и около 50 ключевых слов. Можно вынести списки в отдельный `sources.json` / `keywords.txt`, чтобы добавлять без правки кода. Из интересных источников, которых пока нет: HackerNews (Algolia API), Reddit r/MachineLearning, Substack-блоги отдельных исследователей.

2. **Асинхронность** — фиды тянутся последовательно, а их 15 штук. С `aiohttp` + `asyncio` было бы в 4-5 раз быстрее.

3. **Фильтрация по тегу** — добавить флаг `--tag research` / `--tag industry`, чтобы смотреть только нужную категорию без лишнего шума.

4. **Дедупликация** — разные издания пишут про одни и те же события. Можно сравнивать заголовки через rapidfuzz и группировать похожие новости вместе.

## Структура проекта

```
├── SKILL.md                   # описание скилла
├── README.md
├── requirements.txt
├── fetch_news.py              # основной скрипт
├── .gitignore
├── demo/
│   └── demo.mp4               # запись демонстрации работы в Claude Code
└── .claude/
    └── commands/
        └── news.md            # slash-команда /news
```
