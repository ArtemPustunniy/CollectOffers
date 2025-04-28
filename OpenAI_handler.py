import json
import openai
from config import OPENAI_API_KEY, CUSTOM_PROMPT

openai.api_key = OPENAI_API_KEY


def check_with_openai(message_text: str) -> json:
    try:
        client = openai.OpenAI(api_key=openai.api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": CUSTOM_PROMPT.format(message=message_text)}],
            temperature=0.0
        )

        response_text = response.choices[0].message.content.strip()

        try:
            structured_data = json.loads(response_text)
        except json.JSONDecodeError:
            print(f"Ошибка: OpenAI вернул некорректный JSON: {response_text}")
            return False

        print("Structured Output:", json.dumps(structured_data, indent=4, ensure_ascii=False))

        return structured_data

    except Exception as e:
        print(f"OpenAI API error: {e}")
        return False
