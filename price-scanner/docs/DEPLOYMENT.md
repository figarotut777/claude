# Price-Scanner - Deployment Guide

## Содержание

1. [Локальное развертывание](#локальное-развертывание)
2. [Production развертывание](#production-развертывание)
3. [Конфигурация сервисов](#конфигурация-сервисов)
4. [Мониторинг](#мониторинг)
5. [Troubleshooting](#troubleshooting)

---

## Локальное развертывание

### Требования

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM минимум
- 10GB свободного места на диске

### Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd price-scanner

# 2. Создать .env файл
cp .env.example .env

# 3. Отредактировать .env и добавить API ключи
nano .env

# 4. Запустить все сервисы
docker-compose up -d

# 5. Проверить статус
docker-compose ps

# 6. Просмотреть логи
docker-compose logs -f
```

### Проверка работоспособности

После запуска проверьте доступность сервисов:

```bash
# API Gateway
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Image Search Service
curl http://localhost:8001/health

# Text Search Service
curl http://localhost:8002/health

# URL Parser Service
curl http://localhost:8003/health

# Marketplace Connectors
curl http://localhost:8004/health

# Normalizer Service
curl http://localhost:8005/health
```

---

## Production развертывание

### Подготовка сервера

Рекомендуемые характеристики:
- CPU: 4+ cores
- RAM: 8GB+
- Disk: 50GB+ SSD
- OS: Ubuntu 22.04 LTS или newer

### Установка зависимостей

```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установить Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавить пользователя в группу docker
sudo usermod -aG docker $USER
```

### Production конфигурация

1. Создайте production docker-compose файл:

```bash
cp docker-compose.yml docker-compose.prod.yml
```

2. Измените `docker-compose.prod.yml`:

```yaml
# Добавьте restart policies
services:
  postgres:
    restart: always
  redis:
    restart: always
  api-gateway:
    restart: always
  # ... для всех сервисов

# Используйте volumes для персистентности
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
```

3. Создайте `.env.production`:

```bash
cp .env.example .env.production

# Отредактируйте production переменные
nano .env.production
```

Важные настройки для production:
```env
DEBUG=false
LOG_LEVEL=WARNING
SECRET_KEY=<сгенерируйте случайный ключ>
ALLOWED_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://postgres:<strong-password>@postgres:5432/price_scanner
```

4. Запустите production версию:

```bash
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
```

### Nginx Reverse Proxy

Установите и настройте Nginx:

```bash
sudo apt install nginx -y
```

Создайте конфигурацию `/etc/nginx/sites-available/price-scanner`:

```nginx
upstream api {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API
    location /api {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://api;
    }
}
```

Активируйте конфигурацию:

```bash
sudo ln -s /etc/nginx/sites-available/price-scanner /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL сертификат (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

---

## Конфигурация сервисов

### PostgreSQL

Для production используйте внешнюю БД или настройте резервное копирование:

```bash
# Backup
docker-compose exec postgres pg_dump -U postgres price_scanner > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres price_scanner < backup.sql
```

### Redis

Настройте персистентность в `docker-compose.prod.yml`:

```yaml
redis:
  command: redis-server --appendonly yes --appendfsync everysec
  volumes:
    - redis_data:/data
```

### API Keys

Не храните API ключи в репозитории. Используйте:
- Environment variables
- Docker secrets
- AWS Secrets Manager / Azure Key Vault

---

## Мониторинг

### Логи

Просмотр логов всех сервисов:

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f api-gateway

# Последние 100 строк
docker-compose logs --tail=100 api-gateway
```

### Health Checks

Создайте скрипт мониторинга `scripts/health-check.sh`:

```bash
#!/bin/bash

services=(
    "http://localhost:8000/health"
    "http://localhost:8001/health"
    "http://localhost:8002/health"
    "http://localhost:8003/health"
    "http://localhost:8004/health"
    "http://localhost:8005/health"
)

for service in "${services[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" $service)
    if [ $status -eq 200 ]; then
        echo "✓ $service - OK"
    else
        echo "✗ $service - FAILED (HTTP $status)"
    fi
done
```

### Prometheus + Grafana (опционально)

Добавьте в `docker-compose.prod.yml`:

```yaml
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  restart: always

grafana:
  image: grafana/grafana:latest
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
  volumes:
    - grafana_data:/var/lib/grafana
  restart: always
```

---

## Troubleshooting

### Сервис не запускается

```bash
# Проверить статус
docker-compose ps

# Проверить логи
docker-compose logs <service-name>

# Перезапустить сервис
docker-compose restart <service-name>

# Пересобрать образ
docker-compose build --no-cache <service-name>
docker-compose up -d <service-name>
```

### База данных недоступна

```bash
# Проверить подключение к PostgreSQL
docker-compose exec postgres psql -U postgres -c "SELECT 1"

# Проверить Redis
docker-compose exec redis redis-cli ping
```

### Проблемы с памятью

```bash
# Проверить использование ресурсов
docker stats

# Ограничить память для сервисов в docker-compose.yml
services:
  api-gateway:
    deploy:
      resources:
        limits:
          memory: 512M
```

### Очистка

```bash
# Остановить все контейнеры
docker-compose down

# Удалить volumes (ВНИМАНИЕ: удалит все данные)
docker-compose down -v

# Очистить неиспользуемые образы
docker system prune -a
```

---

## Обновление

```bash
# 1. Сделать backup
docker-compose exec postgres pg_dump -U postgres price_scanner > backup_$(date +%Y%m%d).sql

# 2. Получить последние изменения
git pull

# 3. Пересобрать образы
docker-compose build

# 4. Запустить с новой версией
docker-compose up -d

# 5. Проверить логи
docker-compose logs -f
```

---

## Масштабирование

Для горизонтального масштабирования используйте Docker Swarm или Kubernetes.

### Docker Swarm

```bash
# Инициализировать swarm
docker swarm init

# Развернуть stack
docker stack deploy -c docker-compose.prod.yml price-scanner

# Масштабировать сервис
docker service scale price-scanner_api-gateway=3
```

### Kubernetes

Используйте Helm chart или создайте manifest файлы для каждого сервиса.

---

## Поддержка

Для вопросов и проблем создайте issue в репозитории проекта.
