import asyncio
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from browser_use import Agent
from langchain_openai import ChatOpenAI

# Google Sheets API Authentication
GOOGLE_SHEETS_KEY_PATH = r"C:\Users\admin\browser-use\google_sheets_key.json"  # Update this path
SHEET_NAME = "BrowserUse Results"  # Change this to your actual Google Sheet name

def authenticate_google_sheets():
    """Authenticate and return a Google Sheets client."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_KEY_PATH, scope)
    client = gspread.authorize(creds)
    return client

async def test_browser_use():
    """Run the browser-use agent and extract Google search results."""
    
    print("\n🔹 Starting Browser-Use Agent...")

    # Initialize OpenAI Model
    llm = ChatOpenAI(model="gpt-4o")

    # Create Agent
    agent = Agent(
        task="Search Google for 'SQL tutorial' and return the first result title and link.",
        llm=llm
    )

    # Run Agent
    result = await agent.run()

    print("\n🔥 DEBUG: Full Agent History Structure 🔥\n", result.history)

    # Extract Content
    extracted_content = None
    for action in result.history:
        if hasattr(action, "extracted_content") and action.extracted_content:
            extracted_content = action.extracted_content.strip()
            break

    if not extracted_content:
        print("❌ No valid response received.")
        return

    # Extract Title and Link using regex
    title_match = re.search(r"Title:\s*'(.+?)'", extracted_content)
    link_match = re.search(r"https?://[^\s]+", extracted_content)

    title = title_match.group(1) if title_match else "No Title Found"
    link = link_match.group(0) if link_match else "No Link Found"

    print("\n✅ Extracted Title:", title)
    print("✅ Extracted Link:", link)

    # Store in Google Sheets
    try:
        print("\n🔹 Attempting to authenticate with Google Sheets...")
        client = authenticate_google_sheets()
        sheet = client.open(SHEET_NAME).sheet1  # Access first sheet
        sheet.append_row([title, link])
        print("✅ Data successfully stored in Google Sheets!")
    except Exception as e:
        print(f"❌ Google Sheets Error: {e}")

# Run the function
asyncio.run(test_browser_use())
