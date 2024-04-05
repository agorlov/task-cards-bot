from openai import OpenAI

from config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://openai.a505.ru/v1")

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",  # model="gpt-4-0125-preview"
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming. На русском."}
  ]
)

# https://platform.openai.com/docs/guides/function-calling
tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ]


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
