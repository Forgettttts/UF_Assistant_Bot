import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from notion_client import Client
import locale


# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Initialize Notion API client
notion = Client(auth=NOTION_TOKEN)

# Set the locale to Spanish (Chile)
locale.setlocale(locale.LC_ALL, "es_ES.UTF-8")


def format_currency(value):
    return locale.currency(value, grouping=True)


async def start(update: Update, context):
    keyboard = [
        [
            InlineKeyboardButton(
                "❔ | Consultar UF al día de hoy", callback_data="consulta_uf"
            )
        ],
        [
            InlineKeyboardButton(
                "😽 | Ingresar sueldo de Carito ", callback_data="ingresar_sueldo"
            )
        ],
        [
            InlineKeyboardButton(
                "😽 | Obtener monto a ahorrar de Carito",
                callback_data="calcular_ahorro",
            )
        ],
        [
            InlineKeyboardButton(
                "😼 | Ingresar sueldo de Alan ", callback_data="ingresar_sueldo_alan"
            )
        ],
        [
            InlineKeyboardButton(
                "😼 | Obtener monto a ahorrar de Alan",
                callback_data="calcular_ahorro_alan",
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "😸Hola Carito, selecciona una opción:", reply_markup=reply_markup
    )


async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "calcular_ahorro":
        await calcular_ahorro(update, context, "Caro")
    if query.data == "ingresar_sueldo":
        await pedir_sueldo(update, context)
    if query.data == "calcular_ahorro_alan":
        await calcular_ahorro(update, context, "Alan")
    if query.data == "ingresar_sueldo_alan":
        await pedir_sueldo_alan(update, context)
    elif query.data == "consulta_uf":
        await consulta_uf(update, context)


async def calcular_ahorro(update: Update, context, nombre: str):
    try:
        # Fetch the database (this will return the database properties)
        current_month = datetime.now().strftime("%Y-%m")  # Get YYYY-MM format
        response = notion.databases.query(
            database_id=NOTION_DATABASE_ID,
            filter={
                "property": "Fecha",
                "date": {"on_or_after": current_month + "-01"},
            },
        )
        ahorroMes = response["results"][0]["properties"]["Ahorro " + nombre]["formula"][
            "number"
        ]
        print(f"El ahorro del mes para {nombre} es de {ahorroMes}.\n")
        ahorro_con_formato = format_currency(ahorroMes)
        await update.callback_query.message.reply_text(
            f"😎 El ahorro de este mes para {nombre} es de CLP{ahorro_con_formato}"
        )

    except Exception as e:
        # If there's an error (like permissions or incorrect ID), print the error
        print(f"Error: {e}")


def getValorUF():
    url = "https://mindicador.cl/api/uf"
    response = requests.get(url).json()
    return response["serie"][0]["valor"]


async def consulta_uf(update: Update, context):
    formatted_uf_value = format_currency(getValorUF())
    await update.callback_query.message.reply_text(
        f"🙀 El valor de la UF hoy es de CLP{formatted_uf_value}"
    )


async def pedir_sueldo(update: Update, context):
    await update.callback_query.message.reply_text(
        "😽 Carito, ingresa tu sueldo de este mes, por favor:"
    )
    context.user_data["awaiting_salary"] = True


async def pedir_sueldo_alan(update: Update, context):
    await update.callback_query.message.reply_text(
        "👻 Alan, ingresa tu sueldo de este mes, por favor:"
    )
    context.user_data["awaiting_salary_alan"] = True


# Function to check if salary already exists for the current month
def salary_exists():
    print(f"\n ..:: CONSULTANDO LA BASE DE DATOS EN NOTION ::.. \n")
    current_month = datetime.now().strftime("%Y-%m")  # Get YYYY-MM format
    try:
        query = notion.databases.query(
            database_id=NOTION_DATABASE_ID,
            filter={
                "property": "Fecha",
                "date": {"on_or_after": current_month + "-01"},
            },
        )
    except Exception as e:
        # If there's an error (like permissions or incorrect ID), print the error
        print(f"Error revisando registros existentes: {e}")

    print(f"..:: BUSCANDO REGISTROS EXISTENTES DEL MISMO MES ::.. \n")
    for result in query["results"]:
        entry_date = result["properties"]["Fecha"]["date"]["start"]  # YYYY-MM-DD format
        if entry_date.startswith(current_month):  # Check if date starts with YYYY-MM
            return True
    return False


def update_salary_for_current_month(new_salary: int, persona: str):
    print(f"..:: SE ACTUALIZARÁ REGISTRO DEL MISMO MES ::.. \n")
    current_month = datetime.now().strftime("%Y-%m")  # Get YYYY-MM format

    # Query the database to find the row for the current month
    response = notion.databases.query(
        database_id=NOTION_DATABASE_ID,
        filter={
            "property": "Fecha",
            "date": {
                "on_or_after": current_month + "-01",
            },
        },
    )

    if response["results"]:
        # Assuming there's only one row per month
        page_id = response["results"][0]["id"]

        # Update the row with the new salary
        match persona:
            case "Caro":
                notion.pages.update(
                    page_id=page_id,
                    properties={
                        "Sueldo Caro": {"number": new_salary},
                    },
                )
                print(
                    f"Sueldo actulizado para Caro.\n\tMes: {current_month}.\n\tSueldo nuevo:CLP{format_currency(new_salary)}.\n"
                )
            case "Alan":
                notion.pages.update(
                    page_id=page_id,
                    properties={
                        "Sueldo Alan": {"number": new_salary},
                    },
                )
                print(
                    f"Sueldo actulizado para Alan.\n\tMes: {current_month}.\n\tSueldo nuevo:CLP{format_currency(new_salary)}.\n"
                )
    else:
        print(f"No se encontraron registros del mes {current_month}")


# Function to save salary in Notion
async def save_salary(update: Update, context):

    if not context.user_data.get("awaiting_salary") and not context.user_data.get(
        "awaiting_salary_alan"
    ):
        return
    elif context.user_data.get("awaiting_salary") and not context.user_data.get(
        "awaiting_salary_alan"
    ):
        salary_text = update.message.text
        if not salary_text.isdigit():  # Ensure input is a number
            await update.message.reply_text(
                "⚠️ Por favor, ingresa sólo números, sin puntos ni comas."
            )
            return

        salary = int(salary_text)
        if salary_exists():
            await update.message.reply_text(
                "🔃 Ya existe un registro de sueldo para este mes, se actualizará/complementará el registro."
            )
            print(
                "🔃 Ya existe un registro de sueldo para este mes, se actualizará/complementará el registro."
            )
            update_salary_for_current_month(salary, "Caro")
            await update.message.reply_text(
                f"✅ Se actualizó correctamente el sueldo de este mes de Caro (CLP{format_currency(salary)})."
            )
            context.user_data["awaiting_salary"] = False  # Reset state
            return

        # Add new salary record to Notion
        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Sueldo Caro": {"number": salary},
                "Fecha": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                "Valor UF mes": {"number": getValorUF()},
            },
        )

        await update.message.reply_text(
            f"Se guardó correctamente:\n\n\t✅ | Sueldo de este mes de Caro (CLP{format_currency(salary)}).\n\t✅ | Valor de la UF de este mes(CLP{format_currency(getValorUF())}).\n\nRecuerdale al Alan que ingrese su sueldo👀"
        )
        context.user_data["awaiting_salary"] = False  # Reset state
    elif not context.user_data.get("awaiting_salary") and context.user_data.get(
        "awaiting_salary_alan"
    ):
        salary_text = update.message.text
        if not salary_text.isdigit():  # Ensure input is a number
            await update.message.reply_text(
                "⚠️ Por favor, ingresa sólo números, sin puntos ni comas."
            )
            return

        salary = int(salary_text)
        if salary_exists():
            await update.message.reply_text(
                "🔃 Ya existe un registro de sueldo para este mes, se actualizará/complementará el registro."
            )
            print(
                "🔃 Ya existe un registro de sueldo para este mes, se actualizará/complementará el registro."
            )
            update_salary_for_current_month(salary, "Alan")
            await update.message.reply_text(
                f"✅ Se actualizó correctamente el sueldo de este mes de Alan (CLP{format_currency(salary)})."
            )
            context.user_data["awaiting_salary"] = False  # Reset state
            return

        # Add new salary record to Notion
        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Sueldo Alan": {"number": salary},
                "Fecha": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                "Valor UF mes": {"number": getValorUF()},
            },
        )

        await update.message.reply_text(
            f"Se guardó correctamente:\n\t✅ | Sueldo de este mes de Alan (CLP{format_currency(salary)}).\n\t✅ | Valor de la UF de este mes(CLP{format_currency(getValorUF())}).\nRecuerdale a la Caro que ingrese su sueldo👀"
        )
        context.user_data["awaiting_salary_alan"] = False  # Reset state


# Set up bot and handlers
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_salary))

print("Bot is running...")
app.run_polling()
