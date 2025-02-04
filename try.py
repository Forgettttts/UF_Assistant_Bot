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


# Run the test function
if __name__ == "__main__":
    test_connection()
