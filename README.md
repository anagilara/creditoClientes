# Nexo: directorio de clientes v2

Aplicación web en Python para administrar un directorio de clientes. Usa Flask para servir la interfaz y SQLite para conservar los datos localmente.

## Funcionalidades v2

- Crear clientes con nombre, empresa, correo electrónico, teléfono y notas. El nombre es obligatorio; los demás campos son opcionales.
- Consultar y ordenar el directorio por nombre.
- Buscar por nombre, empresa, correo o teléfono.
- Editar la información de un cliente o eliminarlo con confirmación.
- Ver un resumen con el número de clientes, los que tienen correo y las empresas registradas.
- Proteger las operaciones de escritura con tokens CSRF.

## Estructura del repositorio v2

```text
.
├── app.py                 # Rutas Flask, acceso a SQLite e inicialización del esquema
├── requirements.txt       # Dependencias de la aplicación
├── clientes.db            # Base SQLite local, creada al iniciar (no se versiona)
├── docs/                  # Arquitectura, guía de uso y modelo de datos
├── templates/
│   └── index.html         # Página del directorio y formulario de cliente
├── static/
│   ├── app.js             # Apertura, edición y cierre del formulario
│   └── styles.css         # Estilos adaptables a móvil
└── tests/
	└── test_app.py        # Pruebas de rutas y operaciones CRUD
```

Consulta el [índice de documentación](docs/README.md) para ver la [arquitectura](docs/arquitectura.md), la [guía de uso](docs/uso.md) y el [modelo de datos](docs/modelo-datos.md).

## Ejecutar localmente

Requiere Python 3.10 o posterior. Desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abre http://127.0.0.1:5000. La tabla `clientes` se crea automáticamente en `clientes.db` durante el inicio. La base se mantiene entre reinicios; elimina ese archivo solo si deseas empezar con un directorio vacío.

Para activar el modo de depuración durante el desarrollo:

```bash
FLASK_DEBUG=1 python app.py
```

El modo de depuración está desactivado por defecto.

## Datos y rutas

La tabla `clientes` contiene `id`, `nombre`, `empresa`, `correo`, `telefono`, `notas` y `creado_en`. Los campos de texto opcionales se almacenan como cadenas vacías si no se proporcionan.

| Método | Ruta | Acción |
| --- | --- | --- |
| `GET` | `/` | Muestra el directorio; acepta `?q=texto` para buscar. |
| `POST` | `/clientes/guardar` | Crea un cliente si no recibe `id`, o actualiza el cliente indicado. |
| `POST` | `/clientes/<id>/eliminar` | Elimina el cliente indicado. |

Las rutas de escritura requieren un token CSRF válido y redirigen al directorio después de procesar la solicitud.

## Ejecutar las pruebas

```bash
python -m unittest discover -s tests -v
```

Las pruebas usan bases de datos temporales y cubren el listado, las operaciones CRUD, la búsqueda, el campo obligatorio y la protección CSRF. No modifican `clientes.db`.

## CI/CD en Azure

El workflow `.github/workflows/ci-cd.yml` compila y empaqueta la aplicación y ejecuta los tests en cada pull request y push a `main`. Tras un push a `main` que pase ambos jobs, crea el grupo de recursos, despliega `infra/main.bicep` y publica el paquete en Azure App Service.

Configura estas variables del repositorio en GitHub Actions:

- `AZURE_RESOURCE_GROUP`: grupo de recursos que se creará o reutilizará.
- `AZURE_LOCATION`: región de Azure, por ejemplo `eastus`.
- `AZURE_WEBAPP_NAME`: nombre globalmente único de la Web App, en minúsculas.

Configura estos secretos:

- `AZURE_CREDENTIALS`: credenciales JSON de un principal de servicio con permisos Contributor en la suscripción.
- `APP_SECRET_KEY`: valor aleatorio y privado usado para firmar las sesiones y tokens CSRF.

Bicep crea un App Service Plan Linux Basic (B1) y una Web App con Python 3.12. La base SQLite se guarda en `/home/clientes.db`, dentro del almacenamiento persistente de App Service.

## Configuración para despliegue

- Define `SECRET_KEY` con un valor aleatorio y privado. El valor predeterminado del código es solo para desarrollo local.
- No habilites `FLASK_DEBUG` en producción.
- Ejecuta Flask detrás de un servidor WSGI de producción; el servidor integrado se reserva para desarrollo.
- Conserva y respalda `clientes.db`: contiene los datos de la aplicación y no está incluido en Git.
