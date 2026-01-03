# English Profesor Expert

Sistema completo de enseñanza de inglés con IA, incluyendo un bot de Telegram y un panel web para seguimiento de progreso.

## Características

- **Bot de Telegram** con tutor de IA personalizado (niveles Pre-A1 a C1)
- **Transcripción de voz** con OpenAI Whisper
- **Respuestas en audio** con ElevenLabs TTS
- **Panel web** para visualizar progreso del estudiante
- **Sistema de niveles** con evaluación automática
- **Seguimiento de habilidades**: Speaking, Listening, Reading, Writing, Vocabulary, Grammar
- **Historial completo** de lecciones y conversaciones

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         TRAEFIK                                  │
│            panel.tudominio.com │ api.tudominio.com              │
└─────────────────────────────────────────────────────────────────┘
                │                         │
                ▼                         ▼
        ┌──────────────┐         ┌──────────────────────────┐
        │   Frontend   │         │      Backend (FastAPI)   │
        │   (React)    │◄───────►│  - Telegram Bot          │
        │   Panel      │         │  - AI Agent (LangGraph)  │
        └──────────────┘         │  - Speech Services       │
                                 └──────────────────────────┘
                                            │
                                 ┌──────────┴──────────┐
                                 ▼                     ▼
                          ┌──────────┐          ┌──────────┐
                          │ Postgres │          │  Redis   │
                          └──────────┘          └──────────┘
```

## Requisitos

- Docker y Docker Compose
- Traefik configurado (ya existente en tu servidor)
- Credenciales de API:
  - Telegram Bot Token
  - OpenAI API Key
  - ElevenLabs API Key

## Configuración

### 1. Clonar y configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```env
# Telegram
TELEGRAM_BOT_TOKEN=tu_token_de_telegram

# OpenAI
OPENAI_API_KEY=tu_api_key_de_openai

# ElevenLabs
ELEVENLABS_API_KEY=tu_api_key_de_elevenlabs
ELEVENLABS_VOICE_ID=kC1WIuSSgwH2T8iOV4iJ

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password_seguro
POSTGRES_DB=english_tutor

# Domains (para Traefik)
API_DOMAIN=api.english.tudominio.com
PANEL_DOMAIN=panel.english.tudominio.com

# Security
SECRET_KEY=genera_una_clave_segura_aqui
```

### 2. Crear red de Traefik (si no existe)

```bash
docker network create traefik_proxy
```

### 3. Desplegar en producción

```bash
docker-compose up -d --build
```

### 4. Verificar despliegue

```bash
# Ver logs
docker-compose logs -f backend

# Verificar salud
curl https://api.english.tudominio.com/health
```

## Desarrollo Local

```bash
# Usar docker-compose de desarrollo
docker-compose -f docker-compose.dev.yml up -d --build

# Backend disponible en: http://localhost:8000
# Frontend disponible en: http://localhost:3000
# API docs: http://localhost:8000/docs
```

## Estructura del Proyecto

```
EnglishProfesorExpert/
├── docker-compose.yml          # Producción con Traefik
├── docker-compose.dev.yml      # Desarrollo local
├── .env.example
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/               # Migraciones DB
│   └── app/
│       ├── main.py            # FastAPI app
│       ├── config.py
│       ├── database.py
│       ├── models/            # SQLAlchemy models
│       ├── schemas/           # Pydantic schemas
│       ├── api/               # REST endpoints
│       ├── agent/             # LangGraph tutor
│       ├── telegram/          # Telegram bot
│       └── services/          # Business logic
│
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    └── src/
        ├── App.jsx
        ├── components/
        ├── pages/
        ├── hooks/
        └── context/
```

## Uso del Bot

1. Busca tu bot en Telegram
2. Envía `/start` para comenzar
3. El bot te guiará desde nivel Pre-A1
4. Puedes enviar texto o notas de voz
5. Usa `/progress` para ver tu avance
6. Usa `/panel` para acceder al panel web

## Comandos del Bot

| Comando | Descripción |
|---------|-------------|
| `/start` | Iniciar o reiniciar |
| `/progress` | Ver progreso |
| `/level` | Información del nivel actual |
| `/panel` | Enlace al panel web |
| `/help` | Ayuda |

## Panel Web

El panel muestra:
- Dashboard con estadísticas
- Gráfico radar de habilidades
- Progreso hacia siguiente nivel
- Historial de lecciones
- Recomendaciones personalizadas

## Migraciones de Base de Datos

```bash
# Generar migración
docker-compose exec backend alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
docker-compose exec backend alembic upgrade head
```

## Monitoreo

```bash
# Logs del backend
docker-compose logs -f backend

# Logs de todos los servicios
docker-compose logs -f

# Estado de los contenedores
docker-compose ps
```

## Backup de Base de Datos

```bash
# Crear backup
docker-compose exec postgres pg_dump -U postgres english_tutor > backup.sql

# Restaurar
cat backup.sql | docker-compose exec -T postgres psql -U postgres english_tutor
```

## Tecnologías

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, LangGraph
- **Frontend**: React 18, Vite, TailwindCSS, Recharts
- **Base de datos**: PostgreSQL 16
- **Cache**: Redis 7
- **AI**: OpenAI GPT-4.1-mini, Whisper, ElevenLabs
- **Bot**: python-telegram-bot v21
- **Infraestructura**: Docker, Traefik

## Licencia

Proyecto privado - Todos los derechos reservados.
