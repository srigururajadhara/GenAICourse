
from langchain_openai import ChatOpenAI

# Initialize the OpenAI model
llm = ChatOpenAI(
    model="gpt-4o-mini"
)

# Ask for exactly 5 healthy breakfast ideas
prompt = """
Suggest exactly 5 healthy breakfast ideas.

Format requirements:
- Number the ideas from 1 to 5.
- Write one idea per line.
- Do not include an introduction or conclusion.
- Print only the five breakfast ideas.
"""

# Send prompt to the model
reply = llm.invoke(prompt)

# Print only the response text
print(reply.content)
