from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=1.0,
    max_output_tokens=100,
)

result = model.invoke("Write a 5 line poem on cricket")

print(result.content)
