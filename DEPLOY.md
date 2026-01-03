# Guía de Despliegue en Portainer

## Paso 1: Preparar el servidor

Asegúrate de que tienes:
- Docker instalado
- Portainer funcionando
- Traefik configurado con la red `traefik_proxy`

## Paso 2: Subir el código

Sube todo el proyecto a tu servidor (Git, SCP, etc.):

```bash
# Ejemplo con git
git clone tu-repo /opt/english-profesor
cd /opt/english-profesor
```

## Paso 3: Configurar variables de entorno

```bash
cp .env.example .env
nano .env
```

Configura las siguientes variables **obligatorias**:

```env
# === OBLIGATORIAS ===

# Telegram - Obtén el token de @BotFather
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# OpenAI - https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-...

# ElevenLabs - https://elevenlabs.io/
ELEVENLABS_API_KEY=...

# Base de datos - Usa una contraseña segura
POSTGRES_PASSWORD=tu_password_muy_seguro_aqui

# Seguridad - Genera con: openssl rand -hex 32
SECRET_KEY=tu_clave_secreta_de_32_caracteres

# Dominios para Traefik
API_DOMAIN=api.english.tudominio.com
PANEL_DOMAIN=panel.english.tudominio.com
```

## Paso 4: Crear la red de Traefik (si no existe)

```bash
docker network create traefik_proxy
```

## Paso 5: Desplegar con Docker Compose

### Opción A: Línea de comandos

```bash
cd /opt/english-profesor
docker-compose up -d --build
```

### Opción B: Desde Portainer

1. Ve a **Stacks** → **Add stack**
2. Nombre: `english-profesor`
3. Método: **Upload** o **Repository**
4. Sube el `docker-compose.yml`
5. Añade las variables de entorno en la sección **Environment variables**
6. Click **Deploy the stack**

## Paso 6: Verificar el despliegue

```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs
docker-compose logs -f backend

# Probar API
curl https://api.english.tudominio.com/health
```

## Paso 7: Configurar el Bot de Telegram

El bot se configura automáticamente al iniciar. Verifica que funciona:

1. Busca tu bot en Telegram
2. Envía `/start`
3. Deberías recibir un mensaje de bienvenida

## Configuración DNS

Asegúrate de tener los registros DNS apuntando a tu servidor:

```
api.english.tudominio.com    A    TU_IP_SERVIDOR
panel.english.tudominio.com  A    TU_IP_SERVIDOR
```

## Troubleshooting

### El bot no responde

```bash
# Verificar logs del backend
docker-compose logs backend | grep -i telegram

# Verificar token
docker-compose exec backend env | grep TELEGRAM
```

### Error de base de datos

```bash
# Verificar que postgres está corriendo
docker-compose ps postgres

# Ver logs de postgres
docker-compose logs postgres
```

### El panel no carga

```bash
# Verificar frontend
docker-compose logs frontend

# Verificar que Traefik enruta correctamente
docker-compose logs | grep traefik
```

### Reiniciar todo

```bash
docker-compose down
docker-compose up -d --build
```

## Actualizar la aplicación

```bash
# Bajar cambios
git pull

# Reconstruir y desplegar
docker-compose up -d --build
```

## Backup

```bash
# Backup de base de datos
docker-compose exec postgres pg_dump -U postgres english_tutor > backup_$(date +%Y%m%d).sql

# Backup de volúmenes
docker run --rm -v english-profesor_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```
