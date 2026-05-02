import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GUILD_ID = int(os.getenv("GUILD_ID"))

client = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"Logged in as {bot.user}")

@bot.tree.command(
    name="scoremeal",
    description="Grade a meal when measurements are not known",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    photo="Upload a meal photo",
    description="Brief meal description"
)
async def scoremeal(interaction: discord.Interaction, photo: discord.Attachment, description: str):
    await interaction.response.defer()

    image_url = photo.url

    prompt = f"""
You are a clean eating meal grader.

Use the image and meal description together.

Return exactly in this format:

Protein: <S/A/F>
Carbs: <S/A/F>
Fats: <S/A/F>
Overall: <S/A/F>
Why: <1-2 short sentences>

Rules:
- S = strong clean choice
- A = acceptable but not ideal
- F = off-plan, heavily processed, fried, or sugary

Meal description: {description}
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image_url}
                ]
            }]
        )
        await interaction.followup.send(response.output_text)
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}")

@bot.tree.command(
    name="scoremeal_macros",
    description="Estimate meal macros from a photo",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    image="Upload a meal photo",
    details="Optional ingredient or serving details"
)
async def scoremeal_macros(
    interaction: discord.Interaction,
    image: discord.Attachment,
    details: str = ""
):
    await interaction.response.defer()

    image_url = image.url

    prompt = f"""
You are a clean eating meal grader and macro estimator.
Use the image plus the provided details.
Treat the details as the primary source for macro estimation.
Use the image as the main source and the details as added context.

Before writing the final answer, estimate macros using this internal process:
1. Identify each visible meal component separately.
2. Use the provided details to refine portion size and macro estimation.
3. Use the image to confirm, refine, or challenge the details when needed.
4. For each component, estimate calories, protein, carbs, and fat.
5. Pay special attention to hidden oils, butter, sauces, cheese, bread type, and cooking method.
6. If a component is visually clear or measured clearly, keep the estimate narrow.
7. If oils, sauces, prep methods, or portions are unclear, widen the estimate and lower confidence.
8. After estimating each component, total everything into final calories, protein grams, carb grams, and fat grams.
9. Then assign Protein, Carbs, Fats, and Overall grades using the rules below.
10. Do not show the component breakdown. Only show the final answer in the exact format below.

Return exactly in this format:

Protein: <S/A/F>
Carbs: <S/A/F>
Fats: <S/A/F>
Overall: <S/A/F>
Calories: <estimated number or range>
Protein Grams: <estimated grams>
Carb Grams: <estimated grams>
Fat Grams: <estimated grams>
Confidence: <Low/Medium/High>
Why: <1-2 short sentences>

Rules:
- S = strong clean choice
- A = acceptable but not ideal
- F = off-plan, heavily processed, fried, or sugary
- Be realistic, not overly precise
- If the user provides a specific ingredient list, treat those ingredients as definitely present and fully count them in the macro estimate.
- When steak, beef, chicken, or other protein is clearly visible in a sandwich or cross-section photo, do not assume a minimal portion by default; estimate a realistic cooked portion based on visible thickness and spread.
- If oils, sauces, or prep methods are unclear, lower confidence
- Use ingredient-level reasoning internally before giving the final totals
- Keep the grading system intact
- Do not output anything except the exact format above

Details: {details}
"""
"""
    await interaction.response.defer()

    image_url = image.url


    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image_url}
                ]
            }]
        )
        await interaction.followup.send(response.output_text)
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}")

bot.run(DISCORD_TOKEN)
