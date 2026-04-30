# Dashboard Multi-Agente v4.0

Dashboard web para controlar el Sistema Multi-Agente v4.0 con Claude CEO + Ollama Workers.

## 🚀 Despliegue Rápido en Railway

### Paso 1: Conectar con GitHub
1. Ve a [Railway.app](https://railway.app)
2. Crea cuenta o inicia sesión con GitHub
3. Click en **"New Project"**
4. Selecciona **"Deploy from GitHub repo"**
5. Busca y selecciona: `Toaderz/Interfaz-sistema-multimodelo-`

### Paso 2: Configurar Variables de Entorno
Railway detectará automáticamente el Procfile. Solo necesitas agregar:
- Nada extra, todo está configurado

### Paso 3: Deploy
1. Railway desplegará automáticamente
2. Espera 2-3 minutos
3. Obtendrás una URL como:
   ```
   https://interfaz-sistema-multimodelo-.up.railway.app
   ```

## 🔐 Credenciales de Acceso

- **Usuario**: `Toaderz`
- **Contraseña**: `Doky2010`

## 📁 Estructura del Proyecto

```
├── app.py                 # Servidor Flask principal
├── templates/
│   ├── login.html         # Página de login
│   └── dashboard.html     # Dashboard principal
├── Procfile               # Configuración de Railway
├── railway.toml           # Configuración de build
└── requirements.txt       # Dependencias Python
```

## 🛠️ Tecnologías

- **Backend**: Flask (Python)
- **Frontend**: HTML + Tailwind CSS + JavaScript
- **Estilo**: Dark mode
- **Deploy**: Railway (gratis)

## ⚡ Funcionalidades

- ✅ Login seguro
- ✅ Panel de control en tiempo real
- ✅ Monitor de agentes (Claude CEO, Ollama Research, Ollama Coding, Ollama Validation)
- ✅ Terminal de logs
- ✅ Bandeja de aprobaciones para planes de Claude
- ✅ Métricas de tokens por modelo
- ✅ Gestor de skills
- ✅ Botón HALT para detener sistema

## 📝 Notas

- El dashboard consume APIs REST del backend
- Los datos se actualizan automáticamente cada 5 segundos
- Incluye datos de prueba (mock data) para demostración
