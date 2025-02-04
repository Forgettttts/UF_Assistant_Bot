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

# Load environment variables from .env file
load_dotenv()

# Get your Notion API token from environment variables
NOTION_TOKEN = os.getenv("NOTION_TOKEN")

# Initialize the Notion client
notion = Client(auth=NOTION_TOKEN)

# Replace with your database ID
DATABASE_ID = "your-database-id-here"


def save_salary_to_notion(salary):
    """
    Save salary to Notion database.
    """
    # Get today's date
    today = datetime.today().strftime("%Y-%m-%d")

    # Define the data to send to Notion
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Sueldo Caro": {"number": salary},
            "Date": {"date": {"start": today}},
        },
    }

    # Make the API request to add the new row to the database
    try:
        notion.pages.create(**data)
        print(f"Salary of {salary} saved for {today}.")
    except Exception as e:
        print(f"Error saving salary: {e}")


async def start(update: Update, context):
    """
    Handle the /start command and show buttons.
    """
    # Define the buttons
    keyboard = [
        [InlineKeyboardButton("Consultar UF al día de hoy", callback_data="uf_today")],
        [
            InlineKeyboardButton(
                "Ingresar el sueldo de Caro", callback_data="enter_salary"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with buttons
    await update.message.reply_text(
        "Welcome! Please choose an option:", reply_markup=reply_markup
    )


async def handle_callback(update: Update, context):
    """
    Handle user button clicks.
    """
    query = update.callback_query
    await query.answer()

    if query.data == "enter_salary":
        await query.edit_message_text(text="Please send the salary (number) for Caro:")


async def save_salary(update: Update, context):
    """
    Save the salary entered by the user to the Notion database.
    """
    try:
        # Get the salary from the message
        salary = int(update.message.text)
        save_salary_to_notion(salary)
        await update.message.reply_text(f"Salary of {salary} saved successfully.")
    except ValueError:
        # Handle invalid salary input
        await update.message.reply_text("Please enter a valid salary (number).")


def main():
    """
    Start the Telegram bot and set up the command handlers.
    """
    # Set up the Telegram bot application
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()

    # Command handler for /start
    application.add_handler(CommandHandler("start", start))

    # Callback handler for button clicks
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Message handler for saving salary
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, save_salary)
    )

    # Run the bot
    application.run_polling()


if __name__ == "__main__":
    main()
