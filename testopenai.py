from openai import OpenAI

from config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://openai.a505.ru/v1")

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming. На русском."}
  ]
)

print(completion.choices[0].message)

exit()

# Get Embedding
response = client.embeddings.create(
    input=
    """
Hello, World!
    """,
    model="text-embedding-ada-002"
)

print(response)