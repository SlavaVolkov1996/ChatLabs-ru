#  Быстрый старт
## 1. Клонирование и настройка
#### Клонируйте репозиторий
powershell

    git clone https://github.com/SlavaVolkov1996/ChatLabs-ru.git
    cd C:\MyPythonProjects\pod_git\sobes\ChatLabs-ru

#### Создайте файл с переменными окружения
powershell

    cp .env.example .env

## 2. Настройка переменных окружения (.env)
#### Настройки базы данных
* POSTGRES_DB=postgres_DB
* POSTGRES_USER=slava_volkov_1996
* POSTGRES_PASSWORD=The_Suffering_1996
#### Настройки Django
* DJANGO_SECRET_KEY=django-insecure-yvy977g6q*^gv%sv7af7hk^_i(w%sw3w9y=+89c(w(vwo@0a_2
* DJANGO_DEBUG=True
* ALLOWED_HOSTS=localhost,127.0.0.1,backend
#### Настройки Telegram бота
* BOT_TOKEN=любой токен бота
## 3. Запуск через Docker
powershell

    # Сборка и запуск всех сервисов
    docker-compose up --build -d
    
    # Просмотр логов
    docker-compose logs -f
    
    # Остановка проекта
    docker-compose down

## 4. Создание суперпользователя Django
powershell

    docker-compose exec backend python manage.py createsuperuser

## Краткое описание архитектуры решения
#### Проект построен по микросервисной архитектуре с использованием Docker-контейнеров. Система состоит из шести взаимосвязанных компонентов, взаимодействующих через REST API и брокер сообщений Redis.
1. Backend (Django)
2. Telegram Bot (Aiogram)
3. База данных (PostgreSQL)
4. Message Broker (Redis)
5. Task Queue (Celery)
6. Docker сервисы

### Проблемы

1. Конфликт миграций базы данных - решено очисткой старых миграций(начинал MySQL)
2. Ошибка 500 при обращении к API - исправлено применением корректных миграций(путаница с user, user_id, telegram_user_id))
3. Конфликт обработчиков в Telegram боте - решено реорганизацией логики обработчиков(хотел реализовать прослушку вводимого текста, чтоб в контексте можно было команду выбрать)
4. Проблемы с health check PostgreSQL - исправлено конфигурацией проверки(проблемы при переходе на .env)
5. Настройка часового пояса - единая настройка для всех компонентов(было необычно с этим работать)

