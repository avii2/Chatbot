from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

result = embedding.embed_query("Delhi is the capital of India")

print(str(result))
