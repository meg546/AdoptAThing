import openai
import os
import logging
from dotenv import load_dotenv
import random
from thing import Thing
import requests

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThingGenerator:
    GENDER_OPTIONS = ["Male", "Female", "Non-binary", "Unknown"]

    @staticmethod
    def generate_thing():
        """Generates a new 'Thing' using OpenAI."""
        try:
            name = ThingGenerator.generate_name()
            species = ThingGenerator.generate_species()
            gender = random.choice(ThingGenerator.GENDER_OPTIONS)
            age = random.randint(1, 15)
            description = ThingGenerator.generate_description(name, species)
            images = ThingGenerator.generate_images(name, species)
            return Thing(None, name, species, age, gender, description, images)
        except Exception as e:
            logger.error(f"Error generating Thing: {e}")
            return None

    @staticmethod
    def generate_name():
        prompt = "Generate a unique, creative name for a mysterious sci-fi or fantasy, creature."
        return ThingGenerator.call_ai(prompt)

    @staticmethod
    def generate_species():
        prompt = "Invent a completely unique, original species name for a creature. Do not use real-world species."
        return ThingGenerator.call_ai(prompt)

    @staticmethod
    def generate_description(name, species):
        prompt = (
            f"Create an engaging adoption site description for {name}, a {species}. "
            f"The description should be either fun, mysterious, or heartwarming, depending on the nature of the creature's name and species. "
            f"Use vivid and immersive language to make {name} feel unique and desirable for adoption.\n\n"
            f" **Formatting Rules:**\n"
            f"- The description should be **exactly 1 paragraphs** long.\n"
            f"- Each paragraph should be between **50 to 60 words** to maintain balance.\n"
            f"- The first paragraph should introduce {name} and highlight its most intriguing traits.\n"
            f"- Then it should describe its personality, behavior, or special abilities.\n"
            f"- Finally it should invite potential adopters, emphasizing why {name} would be a perfect companion.\n\n"
            f" **Example Structure:**\n"
            f"- *Meet {name}, a {species} like no other! With shimmering scales and an aura of mystery, this ethereal being captivates all who gaze upon it.*\n"
            f"- *Though {name} may appear enigmatic, it is a playful and affectionate companion, always eager to share stories of distant realms.*\n"
            f"- *Could you be the one to offer {name} a forever home? Open your heart to this extraordinary {species}, and let the adventure begin!*"
        )

        return ThingGenerator.call_ai(prompt)

    @staticmethod
    def generate_images(name, species):
        image_prompts = [
            f"A high-quality Sci-Fi creature, a {species}, standing in a high quality environment befitting its name. No text, no labels, no words in the image.",
        ]
        
        local_image_paths = []
        for idx, prompt in enumerate(image_prompts):
            image_url = ThingGenerator.call_image_ai(prompt)
            print(f"Generated Image URL: {image_url}")  # Debugging

            if image_url:
                local_image_path = ThingGenerator.download_and_save_image(image_url, name, idx)
                print(f"Saved Image: {local_image_path}")  # Debugging
                local_image_paths.append(local_image_path)

        return local_image_paths


    @staticmethod
    def call_ai(prompt, max_tokens=200):
        """Uses OpenAI's GPT to generate text."""
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"AI Text Generation Error: {e}")
            return "Mysterious Creature"

    @staticmethod
    def call_image_ai(prompt):
        """Uses OpenAI's DALL·E to generate images."""
        try:
            response = openai.images.generate(
                model="dall-e-3",
                prompt = prompt + " --ar 16:9 --no text, no labels, no words.",
                n=1,
                size="1024x1024"
            )
            return response.data[0].url
        except Exception as e:
            logger.error(f"Image Generation Error: {e}")
            return "https://via.placeholder.com/300"
        
    @staticmethod
    def download_and_save_image(image_url, name, index):
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                safe_name = name.replace(" ", "_").lower()
                filename = f"static/images/{safe_name}_{index}.png"
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, "wb") as f:
                    f.write(response.content)
                return filename  # Return local file path
        except Exception as e:
            print(f"Failed to download image: {e}")
        return "static/images/placeholder.png"
