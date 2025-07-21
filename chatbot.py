import requests
import config

GEMINI_API_KEY = config.GEMINI_API_KEY1
GEMINI_API_URL = config.GEMINI_URL1

def get_gemini_response(prompt):
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print("Error:", response.status_code, response.text)
            return "Error getting response: " + response.text

    except Exception as e:
        print("Exception:", e)
        return "An error occurred: " + str(e)
