# MC Puertas Platform

Plataforma de registro para la campaña Puertas Mastercard. El staff elige su país al abrir la app y desde ahí registra a los usuarios con su ID, un correo (opcional) y el banco emisor de la tarjeta.

Está hecha con Django y el admin usa [django-unfold](https://github.com/unfoldadmin/django-unfold).

## Cómo funciona

- Hay varios países y cada país tiene sus propios bancos.
- El idioma (español o inglés) depende del país.
- Un ID solo se puede registrar una vez por país. Si ya existe, se muestra la fecha del registro anterior.
- El correo es opcional y puede repetirse.
- El admin siempre está en inglés.

## Levantarlo en local

```bash
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo        # países y bancos de ejemplo
python manage.py createsuperuser
python manage.py runserver
```

- App: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Variables de entorno

Copia `.env.example` a `.env` y ajusta lo que necesites:

| Variable | Para qué sirve |
| --- | --- |
| `DJANGO_SECRET_KEY` | clave secreta de Django |
| `DJANGO_DEBUG` | `True` solo en desarrollo |
| `DJANGO_ALLOWED_HOSTS` | hosts separados por coma |
| `DJANGO_LANGUAGE_CODE` | idioma del admin |
| `DJANGO_TIME_ZONE` | zona horaria |

## Estructura

- `config/`: settings y urls del proyecto
- `registration/`: países, bancos, registros y las vistas del flujo
- `core/`: solo el admin de usuarios y grupos
- `templates/` y `static/`: el diseño (basado en las pantallas de Figma)
- `locale/`: traducciones al español

## Agregar países y bancos

Todo se maneja desde el admin: crea el país (con su idioma) y agrégale los bancos. La URL del país queda como `/<codigo>/`, por ejemplo `/pa/`.

## Traducciones

Si cambias textos en las plantillas o en el código:

```bash
python manage.py makemessages -l es -l en
# edita locale/es/LC_MESSAGES/django.po
python manage.py compilemessages
```

## Tests

```bash
python manage.py test
```
