import os
from notion_client import Client
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get your Notion API token from environment variables
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
# Initialize the Notion client
notion = Client(auth=NOTION_TOKEN)


def test_connection():
    try:
        # Fetch the database (this will return the database properties)

        current_month = datetime.now().strftime("%Y-%m")  # Get YYYY-MM format
        response = notion.databases.query(
            database_id=DATABASE_ID,
            filter={
                "property": "Fecha",
                "date": {"on_or_after": current_month + "-01"},
            },
        )

        # Print the database details to confirm connection
        print("Successfully connected to the database!")
        print("Database details:")
        print(
            json.dumps(
                response["results"][0]["properties"]["Ahorro Caro"]["formula"][
                    "number"
                ],
                indent=4,
            )
        )  # Pretty-print the JSON response

    except Exception as e:
        # If there's an error (like permissions or incorrect ID), print the error
        print(f"Error: {e}")


# # Run the test function
# if __name__ == "__main__":
#     test_connection()
def formato_CLP(monto: float):
    # Redondear el monto, transformarlo a string y revertirlo
    monto_reversed = str(round(monto))[::-1]
    # Dividir el monto en partes de 3 caracteres
    parts = [monto_reversed[i : i + 3] for i in range(0, len(monto_reversed), 3)]

    # Unir las partes con puntos entre ellas y revertir el string
    monto_formatted = ".".join(parts)[::-1]

    # Agregar el signo de peso al principio
    return "$" + monto_formatted


print(formato_CLP(1960000))
print(formato_CLP(750000))
