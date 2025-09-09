import asyncio, websockets, json
from vosk import Model, KaldiRecognizer
import requests

# Load Japanese Vosk model
# Make sure you unzip "vosk-model-small-ja-0.22" into ./model
model = Model("model")

def translate(text):
    try:
        r = requests.post(
            "https://libretranslate.de/translate",
            data={"q": text, "source": "ja", "target": "en"}
        )
        return r.json().get("translatedText", text)
    except Exception as e:
        print("Translation error:", e)
        return text

async def recognize(websocket):
    recognizer = KaldiRecognizer(model, 16000)
    recognizer.SetWords(True)

    async for message in websocket:
        if recognizer.AcceptWaveform(message):
            result = json.loads(recognizer.Result())
            jp_text = result.get("text", "")
            if jp_text:
                en_text = translate(jp_text)
                await websocket.send(json.dumps({"jp": jp_text, "en": en_text}))
        else:
            partial = json.loads(recognizer.PartialResult())
            await websocket.send(json.dumps({"partial": partial.get("partial", "")}))

async def main():
    async with websockets.serve(recognize, "0.0.0.0", 10000):
        print("🚀 Japanese→English Caption Server online at ws://0.0.0.0:10000")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
