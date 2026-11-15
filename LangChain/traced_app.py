
from langchain_openai import ChatOpenAI

# Initialize OpenAI model
llm = ChatOpenAI(
    model="gpt-4o-mini"
)


# Three different prompts
prompts = [
    "Explain Generative AI in simple words.",
    "What is the difference between machine learning and deep learning?",
    "Explain how LangChain helps developers build applications using Large Language Models."
]

# Send prompts and print responses
for index, prompt in enumerate(prompts, start=1):
    print(f"\n{'=' * 50}")
    print(f"RUN {index}")
    print(f"PROMPT: {prompt}")

    response = llm.invoke(prompt)

    print(f"ANSWER: {response.content}")
