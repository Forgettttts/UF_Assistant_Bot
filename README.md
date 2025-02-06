# Bot Telegram Asistente de UF

El bot asistente de uf para telegram es un bot que permite obtener información sobre la UF (Unidad de Fomento) de Chile y como afecta esto al ahorro para la compra de un bien inmueble.

Las funciones del bot son:

- **Obtener el valor de la UF del mes**: Tomando como referencia el valor de la UF al día en el cual el primero de quienes estan ahorrando para el bien inmueble hace su registro de sueldo.
- **Ingresar sueldo del mes**: Se guardará en la base de datos alojada en Notion (*Para tener una interfaz gráfica*).
- **Obtener el valor del ahorro del mes correspondiente**: Calculado con base en la UF del mes y los sueldos de quienes están ahorrando para el bien inmueble.

## Aspectos técnicos 💻

Para ejecutar el bot se debe ejecutar el comando `python main.py`, sin embargo, previo a eso se debe tener instalado python y las librerías necesarias, las cuales pueden ser encontradas en el archivo `requirements.txt` (*los token para acceder al bot de Telegram y Workspace de Notion se deben guardar en un archivo `.env` en la raíz del proyecto, al igual que la ID de la base de datos del Workspace de Notion*).

> :bulb: **Tip:** Para instalar las librerías fácilemnte, ejecutar el comando `pip install -r requirements.txt`.

> :warning: **Advertencia:** Si es que se hace algun cambio en el código, se puede actualizar el archivo `requirements.txt`. *Se puede hacer fácilmente con el comando `pip freeze > requirements.txt`*.

Archivos auxiliares:
- `Dockerfile` → Para poder ejecutar el bot en el servidor de Render dentro de un contenedor.
- `.gitignore` → Para ignorar archivos y carpetas que no se deben subir al repositorio(*archivo `.env`, por ejemplo*).