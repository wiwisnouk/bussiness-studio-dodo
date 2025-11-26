# Инструкция по деплою приложения

## Важно: GitHub Pages не поддерживает FastAPI приложения

GitHub Pages работает только со статическими сайтами (HTML, CSS, JS). Ваше приложение использует FastAPI (серверный фреймворк), поэтому нужен другой хостинг.

## Варианты деплоя

### Вариант 1: Render (Рекомендуется)

**Настройка через веб-интерфейс:**

1. Зайдите на [render.com](https://render.com) и зарегистрируйтесь
2. Нажмите "New +" → "Web Service"
3. Подключите ваш GitHub репозиторий
4. Настройки:
   - **Name**: `bussiness-studio-dodo` (или любое другое)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (или выберите платный)
5. Добавьте переменные окружения:
   - `TOKEN_TG` - токен Telegram бота
   - `TOKEN_TG_REVIEWS` - токен для отзывов
6. Нажмите "Create Web Service"

**Автоматический деплой:**
- Render автоматически деплоит при каждом push в ветку `main`
- GitHub Actions workflow (`.github/workflows/deploy.yml`) уже настроен

### Вариант 2: Railway

1. Зайдите на [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Выберите ваш репозиторий
4. Railway автоматически определит Python приложение
5. Добавьте переменные окружения в настройках проекта

### Вариант 3: Vercel (с serverless функциями)

Требует переработки приложения под serverless архитектуру.

## Настройка GitHub Secrets (для автоматизации)

Если хотите использовать GitHub Actions для автоматического деплоя:

1. Зайдите в ваш репозиторий на GitHub
2. Settings → Secrets and variables → Actions
3. Добавьте необходимые секреты (например, `RENDER_API_KEY`)

## Проверка деплоя

После настройки:
1. Сделайте commit и push в ветку `main`
2. Проверьте логи деплоя на выбранной платформе
3. Откройте URL вашего приложения

## Локальный запуск

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Приложение будет доступно по адресу: `http://localhost:8000`

