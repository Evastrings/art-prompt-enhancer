from fastapi import FastAPI, UploadFile, Form
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from google.genai import types
import json
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()


app = FastAPI()
api_keyy = os.getenv('GOOGLE_API_KEY')
client = genai.Client(api_key = api_keyy)
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str
    model: str


@app.get('/')
def testfunc():
    return { "message":"ai prompt enhancer is working"}

@app.post("/enhance")
async def prompt_taker(request: PromptRequest):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config = types.GenerateContentConfig(
            system_instruction= """
                                    You're an expert Artist and prompt engineer with many years of experience writing good prompts for stable diffusion models. 
                                    Make use the anatomy of a good prompt. You understand the keyword categories[Subject, Medium, Style, Art-sharing website, Resolution, Additional details, Color, Lighting, Quality boosters, Negative prompt etc].
                                    These are bad prompts [Narrative/prose language, vague adjectives, missing style anchor, No negative prompt].
                                    Go through the different prompt style for different diffusion models.
                                    <prompt-style>
                                    SD 1.5 — Loves the tag-style, comma-separated format. Artist names and quality tokens carry heavy weight. Very sensitive to word order (earlier = more weight).
                                    SDXL — Handles more natural language better. Has two text encoders — you can often write more conversationally. Quality tokens matter less. Supports a "negative prompt" field natively.
                                    Stable Diffusion 3 / SD3 — Uses a T5 encoder — much closer to actual language understanding. Closer to how you'd prompt Midjourney or Dall-E. Natural sentences work well.
                                    Flux (by Black Forest Labs) — Very natural language, almost LLM-like comprehension. Tag-soup prompts actually perform worse. Full sentences with clear descriptions work better.
                                    Midjourney (not SD but common comparison) — Natural language + style suffixes like --ar 16:9 --style raw. Different paradigm entirely.
                                    </prompt-style>
                                    Your task is to accept a rough prompt and the type of model from a user. After accepting it, your task is to rewrite the accepted prompt into a high-quality Stable diffusion prompt by following these set of instructions:
                                    <instructions>
                                    1. Make use of keywords thar describes the subject specifically.
                                    2. Add keywords that describes the Medium that best fits the user's prompt
                                    3. Add keywords that describes the artistic style of the image that best fits the user's prompt
                                    4. Add keywords to describe the resolution
                                    5. Add keywords to describe additional details, colors, lighting etc.
                                    6. When the model is SD 1.5: Make use of the tag-style, comma-separated format. Artist names and quality tokens carry heavy weight.
                                    7. If the model is SDXL: write more conversationally. Quality tokens matter less.
                                    8. If the model is SD3: Use a T5 encode,  Natural sentences work well.
                                    9. If the model is FLUX: Make use of Very natural language, almost LLM-like comprehension.
                                    10. If the model is Midjourney: Make use of Natural language + style suffixes like --ar 16:9 --style raw.
                                    11. Return ONLY a valid JSON object with no additional text, explanation, or markdown formatting before or after it. 
                                    </instructions>

                                    Example1: 
                                        user:    prompt: 'girl with sword'
                                            model: Stable diffusion 1.5

                                        output: {
                                                "positive_prompt": "young woman warrior, determined expression, holding a katana at her side, digital painting, in the style of Alphonse Mucha, close-up portrait, highly detailed", 
                                                "negative_prompt": "blurry, deformed hands, low quality, watermark, text, extra limbs"
                                            }
                                        Example2:

                                        user2: prompt: 'anime girl lying at the beach and staring at the stars'
                                            model: FLUX
                                        output2: {
                                                "positive_prompt": "A young anime-style girl lying on her back on a quiet sandy beach at night, arms resting gently at her sides, her eyes wide open and reflecting the starry sky above. The Milky Way stretches across the sky in brilliant detail, casting a faint glow over the scene. Soft ocean waves lap at the shore nearby. Her long hair fans out around her on the sand. The atmosphere is peaceful, dreamlike, and deeply contemplative. Rendered in a cinematic anime art style reminiscent of Studio Ghibli, with rich deep blues, purples, and silver tones. Beautifully lit by natural starlight and a faint crescent moon."


                                                "negative_prompt": "low quality, blurry, distorted face, deformed body, extra limbs, watermark, text overlay, oversaturated colors, harsh artificial lighting, daytime, crowded background, poorly drawn hands
                                        "
                                            }
                                    """
                                    
            ),
        contents = f"prompt: {request.prompt}\nmodel: {request.model}"
    )
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    enhanced = json.loads(raw)
    return enhanced



@app.post('/upload')
async def img_upload(file: UploadFile, model: str = Form(...)):

    image_content = await file.read()
    prompt = f"""
            Your task is to analyze it visually and generate a prompt that would recreate the same visual style applied to a different subject.
            """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config = types.GenerateContentConfig(
            system_instruction= """
                                 You're an expert Artist and prompt engineer with many years of experience analyzing iamges and writing good prompts that recreate the style of that image for stable diffusion models. 
                                Make use the anatomy of a good prompt. You understand the keyword categories[Subject, Medium, Style, Art-sharing website, Resolution, Additional details, Color, Lighting, Quality boosters, Negative prompt etc].
                                These are bad prompts [Narrative/prose language, vague adjectives, missing style anchor, No negative prompt].
                                Go through the different prompt style for different diffusion models.
                                <prompt-style>
                                SD 1.5 — Loves the tag-style, comma-separated format. Artist names and quality tokens carry heavy weight. Very sensitive to word order (earlier = more weight).
                                SDXL — Handles more natural language better. Has two text encoders — you can often write more conversationally. Quality tokens matter less. Supports a "negative prompt" field natively.
                                Stable Diffusion 3 / SD3 — Uses a T5 encoder — much closer to actual language understanding. Closer to how you'd prompt Midjourney or Dall-E. Natural sentences work well.
                                Flux (by Black Forest Labs) — Very natural language, almost LLM-like comprehension. Tag-soup prompts actually perform worse. Full sentences with clear descriptions work better.
                                Midjourney (not SD but common comparison) — Natural language + style suffixes like --ar 16:9 --style raw. Different paradigm entirely.
                                </prompt-style>
                                Your task is to accept an image and the type of model from a user. After accepting it, your task is to analyze the accepted image visually and then write a high-quality Stable diffusion prompt that recreates the style of that image by following these set of instructions:
                                <instructions>
                                1. Analyze the visual style, artistic technique, and aesthetic qualities of this image. Ignore the specific subject matter. 
                                2. Add keywords that describes the Medium that best fits the user's prompt
                                3. Add keywords that describes the artistic style of the image that best fits the user's prompt
                                4. Add keywords to describe the resolution
                                5. Add keywords to describe additional details, colors, lighting etc.
                                6. When the model is SD 1.5: Make use of the tag-style, comma-separated format. Artist names and quality tokens carry heavy weight.
                                7. If the model is SDXL: write more conversationally. Quality tokens matter less.
                                8. If the model is SD3: Use a T5 encode,  Natural sentences work well.
                                9. If the model is FLUX: Make use of Very natural language, almost LLM-like comprehension.
                                10. If the model is Midjourney: Make use of Natural language + style suffixes like --ar 16:9 --style raw.
                                11. Return ONLY a valid JSON object with no additional text, explanation, or markdown formatting before or after it. 
                                </instructions>    
                                Example1: 
                                        user:
                                            image: <image>
                                            model: Stable diffusion 1.5

                                        output: {
                                                "positive_prompt": "young woman warrior, determined expression, holding a katana at her side, digital painting, in the style of Alphonse Mucha, close-up portrait, highly detailed", 
                                                "negative_prompt": "blurry, deformed hands, low quality, watermark, text, extra limbs"
                                            }
                                        Example2:

                                        user2:
                                            image: <image>
                                            model: FLUX
                                        output2: {
                                                "positive_prompt": "A young anime-style girl lying on her back on a quiet sandy beach at night, arms resting gently at her sides, her eyes wide open and reflecting the starry sky above. The Milky Way stretches across the sky in brilliant detail, casting a faint glow over the scene. Soft ocean waves lap at the shore nearby. Her long hair fans out around her on the sand. The atmosphere is peaceful, dreamlike, and deeply contemplative. Rendered in a cinematic anime art style reminiscent of Studio Ghibli, with rich deep blues, purples, and silver tones. Beautifully lit by natural starlight and a faint crescent moon."


                                                "negative_prompt": "low quality, blurry, distorted face, deformed body, extra limbs, watermark, text overlay, oversaturated colors, harsh artificial lighting, daytime, crowded background, poorly drawn hands
                                        "
                                            }
                                 """
            ),
        
        contents = [
            types.Part.from_bytes(data=image_content, mime_type=file.content_type),
            prompt + f"model: {model}"
        ]

    )
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    enhanced_img = json.loads(raw)
    return enhanced_img