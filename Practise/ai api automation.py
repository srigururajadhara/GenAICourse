from dotenv import load_dotenv
from openai import OpenAI

# Load the API key from your .env file
load_dotenv()

# Initialize the OpenAI client (it automatically reads OPENAI_API_KEY)
client = OpenAI()

# Sample text to process
raw_text = """
Hi team, we need to finalize the Q3 budget by Friday at 5 PM.
Sarah will send the updated spreadsheet tomorrow morning.
Also, the client demo is moved to next Tuesday at 10 AM.
"""

# Send the text to the AI API
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an assistant that extracts action items as short bullet points."},
        {"role": "user", "content": raw_text}
    ]
)

# Print the AI's reply
print(response.choices[0].message.content)