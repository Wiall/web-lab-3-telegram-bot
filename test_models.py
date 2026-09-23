import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Перевірка доступності Gemini-моделей...\n")

for model in client.models.list():
    model_name = model.name

    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Відповідай одним словом: OK",
        )

        print(f"[OK]       {model_name}")
        print(f"           {response.text.strip()}")

    except Exception as error:
        error_text = str(error).replace("\n", " ")

        if "503" in error_text:
            print(f"[503]      {model_name} — тимчасово перевантажена")

        elif "429" in error_text:
            print(f"[429]      {model_name} — ліміт запитів")

        elif "404" in error_text:
            print(f"[404]      {model_name} — недоступна")

        else:
            print(f"[ERROR]    {model_name} — {error_text[:150]}")

print("\nПеревірку завершено.")