import openai
import os
import logging
from dotenv import load_dotenv
import random
from thing import Thing

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
        """Uses AI to generate a unique name for a Thing."""
        prompt = "Generate a unique, creative name for a mysterious sci-fi or fantasy, creature."
        return ThingGenerator.call_ai(prompt)

    @staticmethod
    def generate_species():
        """Uses AI to generate a completely new, fictional species."""
        prompt = "Invent a completely unique, original species name for a creature. Do not use real-world species."
        return ThingGenerator.call_ai(prompt)

    @staticmethod
    def generate_description(name, species):
        """Uses AI to create a brief description of the creature."""
        prompt = f"Describe {name}, a {species}, in a fun and engaging way for an adoption listing. Make it sound friendly and exciting."
        return ThingGenerator.call_ai(prompt)

    @staticmethod
    def generate_images(name, species):
        """Uses AI image model to generate images."""
        image_prompts = [
            f"A high-quality Sci-Fi creature, a {species}, standing in a natural environment. No text, no labels, no words in the image.",
            f"A close-up portrait of a {species}, in a vibrant setting, highly detailed. No text or symbols in the image."
        ]
        return [ThingGenerator.call_image_ai(prompt) for prompt in image_prompts]

    @staticmethod
    def call_ai(prompt, max_tokens=50):
        """Uses OpenAI's GPT to generate text (Updated for OpenAI v1.0+)."""
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"AI Text Generation Error: {e}")
            return "Mysterious Creature"

    @staticmethod
    def call_image_ai(prompt):
        """Uses OpenAI's DALL·E to generate images (Updated for OpenAI v1.0+)."""
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
