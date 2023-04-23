# ChatGPT <img src="https://github.com/acheong08/ChatGPT/blob/main/logo.png?raw=true" width="15%"></img>

[English](./README.md) - [中文](./README_zh.md) - Spanish -  [日本語](./README_ja.md)

[![PyPi](https://img.shields.io/pypi/v/revChatGPT.svg)](https://pypi.python.org/pypi/revChatGPT)
[![Plataforma_de_Soporte](https://img.shields.io/pypi/pyversions/revChatGPT)](https://pypi.python.org/pypi/revChatGPT)
[![Descargas](https://static.pepy.tech/badge/revchatgpt)](https://pypi.python.org/pypi/revChatGPT)

API de ingeniería reversa para ChatGPT de OpenAI. Extensible para chatbots y más.

[![](https://github.com/acheong08/ChatGPT/blob/main/docs/view.gif?raw=true)](https://pypi.python.org/pypi/revChatGPT)

> ## Apoya mi trabajo
>
> Puedes colaborar con Pull Requests corrigiendo mi código imperfecto.
>
> [![Apoyo](https://ko-fi.com/img/githubbutton_sm.svg)](https://www.youtube.com/watch?v=dQw4w9WgXcQ)

> #### Servidor de Discord: https://discord.gg/9K2BvbXEHT

# Instalación

```
python -m pip install --upgrade revChatGPT
```

### Soporte para versiones de Python

- Mínimo - Python3.9
- Recomendado - Python3.11+

<details>

  <summary>

# V1 (ChatGPT Estándar)

Debido al reciente endurecimiento de la seguridad de OpenAI, el endpoint predeterminado de este API se ha cambiado a uno proporcionado por @pengzhile. No es de código abierto y la privacidad no está garantizada. Úsalo bajo tu propio riesgo. Estoy trabajando en una implementación de código abierto con los últimos cambios, pero eso podría llevar un tiempo.

</summary>

## Límites de peticiones
- Servidor Proxy: 5 peticiones por cada 10 segundos
- OpenAI: 50 peticiones por hora para cada cuenta

## Configuración

1. Crear Cuenta en [OpenAI's ChatGPT](https://chat.openai.com/)
2. Guarde su correo electrónico y contraseña

### Método de autentificación: (Choose 1)

#### - Email / Contraseña de

> _Actualmente no funciona para usuarios gratuitos de ChatGPT. Ejecuta `export PUID="..."` en el terminal si tienes una cuenta Plus. El PUID es un cookie de navegador llamado `_puid`_
> No está disponible para cuentas con login por Google/Microsoft.
```json
{
  "email": "email",
  "password": "tu contraseña"
}
```

#### - Token de Acceso

> por favor lee esto primero!
https://chat.openai.com/api/auth/session

```json
{
  "access_token": "<token de acceso de openai>"
}
```

#### - Configuración Opcional:

```json
{
  "conversation_id": "UUID...",
  "parent_id": "UUID...",
  "proxy": "...",
  "paid": false,
  "collect_analytics": true,
  "model": "gpt-4"
}
```

La recolección de datos para análisis de OpenAI está deshabilitada de forma predeterminada. Establezca `collect_analytics` en `true` para habilitarlo.

3. Guardar esto en un archivo json en `$HOME/.config/revChatGPT/config.json`
4. Si está utilizando Windows, deberá crear una variable de entorno llamada `HOME` y establecerla en su perfil de inicio para que el script pueda ubicar el archivo config.json.

## Uso

### Línea de comando

`python3 -m revChatGPT.V1`

```
        ChatGPT - Una interfaz de línea de comandos para ChatGPT de OpenAI (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
Escribe '!help' para mostrar una lista completa de comandos
Logging in...
You:
(Presiona Esc seguido de Enter para terminar)
```

La interfaz de línea de comandos admite entradas multilinea y permite la navegación con las flechas del teclado. Además, también puede autocompletar la entrada si encuentra Prompts similares en el historial. Para finalizar presione `Esc` y luego `Enter` ya que únicamente `Enter` se usa para crear una nueva línea en el modo multilínea.

Establezca la variable de entorno `NO_COLOR` a `true` para deshabilitar el texto colorido.

### API de desarrollador


#### Ejemplo básico (streamed):

```python
from revChatGPT.V1 import Chatbot
chatbot = Chatbot(config={
  "access_token": "<your access_token>"
})
print("Chatbot: ")
prev_text = ""
for data in chatbot.ask(
    "Hello world",
):
    message = data["message"][len(prev_text) :]
    print(message, end="", flush=True)
    prev_text = data["message"]
print()
```

#### Ejemplo básico (resultado único):

```python
from revChatGPT.V1 import Chatbot
chatbot = Chatbot(config={
  "access_token": "<your access_token>"
})
prompt = "how many beaches does portugal have?"
response = ""
for data in chatbot.ask(
  prompt
):
    response = data["message"]
print(response)
```

#### Todos los métodos de la API

Referirse a [wiki](https://github.com/acheong08/ChatGPT/wiki/) for advanced developer usage.

</details>

<summary>

# API oficial V3 (Chat API)

> Lanzado recientemente por OpenAI
>
> - De pago

</summary>

Obtén clave API de https://platform.openai.com/account/api-keys

## Línea de comando

`python3 -m revChatGPT.V3 --api_key <api_key>`

```
  $ python3 -m revChatGPT.V3 --help

    ChatGPT - Official ChatGPT API
    Repo: github.com/acheong08/ChatGPT

Escriba '!help' para mostrar una lista completa de comandos
Presione Esc seguido de Enter o Alt+Enter para enviar un mensaje.

usage: V3.py [-h] --api_key API_KEY [--temperature TEMPERATURE] [--no_stream] [--base_prompt BASE_PROMPT]
             [--proxy PROXY] [--top_p TOP_P] [--reply_count REPLY_COUNT] [--enable_internet]
             [--config CONFIG] [--submit_key SUBMIT_KEY] [--model {gpt-3.5-turbo,gpt-4,gpt-4-32k}]
             [--truncate_limit TRUNCATE_LIMIT]

opciones:
  -h, --help            mostrar este mensaje de ayuda y salir
  --api_key API_KEY     Clave API de OpenAI
  --temperature TEMPERATURE
                        Temperatura de respuesta
  --no_stream           Deshabilitar transmisión
  --base_prompt BASE_PROMPT
                        Indicación base para chatbot
  --proxy PROXY         Dirección proxy
  --top_p TOP_P         Top p para respuesta
  --reply_count REPLY_COUNT
                        Número de respuestas para cada mensaje
  --enable_internet     Permitir que ChatGPT busque en Internet
  --config CONFIG       Ruta al archivo json de configuración V3
  --submit_key SUBMIT_KEY
                        Clave de envío personalizada para chatbot. Para obtener más información sobre las claves, consulte LÉAME
  --model {gpt-3.5-turbo,gpt-4,gpt-4-32k}
  --truncate_limit TRUNCATE_LIMIT
```

## API de desarrollador

### Ejemplo básico

```python
from revChatGPT.V3 import Chatbot
chatbot = Chatbot(api_key="<api_key>")
chatbot.ask("Hello world")
```

### Ejemplo de transmisión

```python
from revChatGPT.V3 import Chatbot
chatbot = Chatbot(api_key="<api_key>")
for data in chatbot.ask_stream("Hello world"):
    print(data, end="", flush=True)
```

</details>

# Awesome ChatGPT

[Más proyectos recomendados](https://github.com/stars/acheong08/lists/awesome-chatgpt)

Si tienes un proyecto interesante que desearias agregar a la lista, agrega un Issue en este repositorio de Github.

# Descargos de responsabilidad

Este no es un producto oficial de OpenAI. Este es un proyecto personal y no está afiliado a OpenAI de ninguna manera. No me demandes.

## Colaboradores

Este proyecto existe gracias a todas las personas que contribuyen.

<a href="https://github.com/acheong08/ChatGPT/graphs/contributors">
<img src="https://contrib.rocks/image?repo=acheong08/ChatGPT" />
</a>

## Créditos adicionales

- Codificando mientras escuchas [esta increíble canción](https://www.youtube.com/watch?v=VaMR_xDhsGg) por [virtualharby](https://www.youtube.com/@virtualharby)
