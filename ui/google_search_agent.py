import asyncio
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from browser_use import Agent
from langchain_openai import ChatOpenAI
import os

# --- Google Sheets API Authentication ---
GOOGLE_SHEETS_KEY_PATH = r"C:\Users\admin\browser-use\google_sheets_key.json"  # YOUR CORRECT PATH
SHEET_NAME = "BrowserUse Results"  # YOUR CORRECT SHEET NAME

# --- OpenAI API Key ---
# Set your OpenAI API key as an environment variable (you still need to do this)

# --- Browser Driver (ChromeDriver) ---
# Either have ChromeDriver in your PATH or specify the path here:
# chromedriver_path=r"C:\path\to\your\chromedriver.exe"

def authenticate_google_sheets():
    """Authenticate and return a Google Sheets client."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_KEY_PATH, scope)
    client = gspread.authorize(creds)
    return client

async def test_browser_use():
    """Run the browser-use agent and extract Google search results."""

    print("\n🔹 Starting Browser-Use Agent...")

    # Initialize OpenAI Model (make sure OPENAI_API_KEY is set)
    llm = ChatOpenAI(model="gpt-4o")

    # Create Agent
    agent = Agent(
        task="Search Google for 'SQL tutorial' and return the first result title and link.",
        llm=llm,
        # chromedriver_path=r"C:\path\to\your\chromedriver.exe"  # Uncomment and specify path if needed
        headless=True #Change this to True if you want to run the code in headless mode
    )

    print("🔹 Agent Created. About to run...")

    try:
        result = await agent.run()
        print("🔹 Agent Run Completed.")

        # Check if the result is None or empty
        if result is None or not result.history:
            print("❌ Agent returned no results.")
            return

        print("\n🔥 DEBUG: Full Agent History Structure 🔥\n", result.history)

        # Extract Content
        extracted_content = None
        for action in result.history:
            if hasattr(action, "result"):
                for a in action.result:
                    if hasattr(a, "extracted_content") and a.extracted_content:
                        extracted_content = a.extracted_content.strip()
                        break

        if not extracted_content:
            print("❌ No valid response received.")
            return

        # Extract Title and Link using regex
        title_match = re.search(r"\'(.*?)\'", extracted_content)
        link_match = re.search(r"https?://[^\s]+", extracted_content)

        title = title_match.group(1) if title_match else "No Title Found"
        link = link_match.group(0) if link_match else "No Link Found"

        print("\n✅ Extracted Title:", title)
        print("\n✅ Extracted Link:", link)

        # Store in Google Sheets
        try:
            print("\n🔹 Attempting to authenticate with Google Sheets...")
            client = authenticate_google_sheets()
            print("✅ Client:", client)

            sheet = client.open(SHEET_NAME).sheet1  # Access first sheet
            print("✅ Sheet:", sheet)

            sheet.append_row([title, link])
            print("✅ Data successfully stored in Google Sheets!")
        except Exception as e:
            print(f"❌ Google Sheets Error: {e}")

    except Exception as e:
        print(f"❌ Error during agent.run(): {e}")

# Run the function
asyncio.run(test_browser_use())