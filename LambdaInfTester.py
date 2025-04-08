from openai import OpenAI
import os
# OpenAI Access
def get_openai_api_key():
    try:
        return os.getenv("OPENAI_API_KEY")
    except Exception as e:
        print(f'Error retrieving OpenAI API Key: {e}')


openai_api_key = get_openai_api_key()
openai_api_base = "https://api.lambda.ai/v1"
# https://cloud.lambda.ai/api/v1/instances

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

model = "llama-4-maverick-17b-128e-instruct-fp8"

chat_completion = client.chat.completions.create(
    messages=[{
        "role": "system",
        "content": "You are an expert conversationalist who responds to the best of your ability."
    }, {
        "role": "user",
        "content": "Who won the world series in 2020?"
    }, {
        "role":
        "assistant",
        "content": "The Los Angeles Dodgers won the World Series in 2020."
    }, {
        "role": "user",
        "content": "Where was it played?"
    }],
    model=model,
)

print(chat_completion)