import os
from groq import Groq

print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY"))
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print("Cliente inicializado com sucesso")