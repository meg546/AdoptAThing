import sys
sys.path.append("Code")
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from Code.thing_generator import ThingGenerator  # Import AI Thing Generator
from Code.thing import Thing  # Import Thing model

app = Flask(__name__)

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('database/petadoption.db')
    conn.row_factory = sqlite3.Row  # Enables dictionary-like access to rows
    return conn

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# function to generate pets
@app.route('/generate_things', methods=['POST'])
def generate_things():
    """Generates multiple AI-based 'Things' and stores them in the database."""
    num_things = int(request.args.get("count", 1))  # Default to 1 if not specified

    generated_things = []
    conn = get_db_connection()
    cursor = conn.cursor()

    for _ in range(num_things):
        thing = ThingGenerator.generate_thing()
        if thing:
            cursor.execute(
                'INSERT INTO things (name, species, age, gender, description) VALUES (?, ?, ?, ?, ?)',
                (thing.name, thing.species, thing.age, thing.gender, thing.description)
            )
            thing_id = cursor.lastrowid

            # Save images
            for img_url in thing.images:
                cursor.execute('INSERT INTO thing_images (thing_id, image_url) VALUES (?, ?)', (thing_id, img_url))

            conn.commit()
            generated_things.append(thing.to_dict())

    conn.close()
    return jsonify({"generated_things": generated_things}), 201


@app.route('/pets')
def pets():
    conn = get_db_connection()
    
    pets = conn.execute('SELECT * FROM pets').fetchall()
    print(f"Pets: {pets}")

    things = conn.execute('SELECT * FROM things').fetchall()
    print(f"Things: {things}")

    things_list = []
    for thing in things:
        thing_id = thing['id']
        images = conn.execute('SELECT image_url FROM thing_images WHERE thing_id = ?', (thing_id,)).fetchall()
        image_urls = [img['image_url'] for img in images]
        things_list.append({
            "id": thing['id'],
            "name": thing['name'],
            "species": thing['species'],
            "age": thing['age'],
            "gender": thing['gender'],
            "description": thing['description'],
            "images": image_urls
        })
    
    print(f"Processed AI Things: {things_list}")

    conn.close()
    return render_template('pets.html', pets=pets, things=things_list)


# Pet or AI Thing Detail Page
@app.route('/pet/<int:pet_id>')
def pet_detail(pet_id):
    conn = get_db_connection()
    
    # Check if the pet is a real pet
    pet = conn.execute('SELECT * FROM pets WHERE id = ?', (pet_id,)).fetchone()
    
    if pet is None:
        # If not found, check if it's an AI-generated Thing
        thing = conn.execute('SELECT * FROM things WHERE id = ?', (pet_id,)).fetchone()
        if thing is None:
            conn.close()
            return "Pet or Thing not found", 404
        
        # Fetch images for the AI Thing
        images = conn.execute('SELECT image_url FROM thing_images WHERE thing_id = ?', (pet_id,)).fetchall()
        image_urls = [img['image_url'] for img in images]

        conn.close()
        return render_template('pet_detail.html', pet=thing, images=image_urls, is_ai=True)

    conn.close()
    return render_template('pet_detail.html', pet=pet, is_ai=False)

# Adoption Request Page (for real pets & AI Things)
@app.route('/adopt/<int:pet_id>', methods=['GET', 'POST'])
def adopt_pet(pet_id):
    conn = get_db_connection()
    
    # Check if it's a real pet
    pet = conn.execute('SELECT * FROM pets WHERE id = ?', (pet_id,)).fetchone()
    
    if pet is None:
        # Check if it's an AI-generated Thing
        thing = conn.execute('SELECT * FROM things WHERE id = ?', (pet_id,)).fetchone()
        if thing is None:
            conn.close()
            return "Pet or Thing not found", 404
        pet = thing  # Treat as a pet for template compatibility

    if request.method == 'POST':
        adopter_name = request.form['name']
        adopter_email = request.form['email']
        conn.execute('INSERT INTO adoption_requests (pet_id, adopter_name, adopter_email) VALUES (?, ?, ?)',
                     (pet_id, adopter_name, adopter_email))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('adopt.html', pet=pet)

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
