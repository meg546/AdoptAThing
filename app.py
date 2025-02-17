import sys
sys.path.append("Code")
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import sqlite3
from Code.thing_generator import ThingGenerator  # Import AI Thing Generator
from Code.thing import Thing  # Import Thing model
from werkzeug.security import generate_password_hash, check_password_hash


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

@app.route('/generate_thing', methods=['POST'])
def generate_thing():
    data = request.get_json()
    count = data.get("count", 1)  # Default to 1 if not provided
    
    if count < 1:
        return jsonify({"error": "Count must be at least 1"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    created_things = []
    
    for _ in range(count):
        new_thing = ThingGenerator.generate_thing()

        if new_thing is None or new_thing.name == "Unknown Creature":
            print(f"⚠️ Skipping Thing due to AI failure")
            continue

        print(f"🔹 Inserting Thing: {new_thing.name} - {new_thing.species}")
        print(f"🔹 Full Description Before Insert: {new_thing.description}")

        formatted_description = new_thing.description.replace("\n", " ")

        cursor.execute('INSERT INTO things (name, species, age, gender, description) VALUES (?, ?, ?, ?, ?)',
                       (new_thing.name, new_thing.species, new_thing.age, new_thing.gender, formatted_description))
        thing_id = cursor.lastrowid

        image_urls = []
        for image_path in new_thing.images:
            cursor.execute('INSERT INTO thing_images (thing_id, image_url) VALUES (?, ?)', (thing_id, image_path))
            image_urls.append(image_path)

        created_things.append({
            "id": thing_id,
            "name": new_thing.name,
            "species": new_thing.species,
            "age": new_thing.age,
            "gender": new_thing.gender,
            "description": new_thing.description,
            "images": image_urls
        })

    conn.commit()
    conn.close()

    if not created_things:
        return jsonify({"error": "No valid Things were generated"}), 500

    return jsonify({"things": created_things}), 201


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


app.secret_key = '123456'
# route to login as an exisiting user
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        user = cursor.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']  # Store username in session
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!')
            return redirect(url_for('login'))

    return render_template('login.html')




# route to register as a user
@app.route('/register', methods =['GET','POST'])
def register():

    # post method that is sending info into database
    if request.method == 'POST':

        # get info from the form in register.html
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password)

        # SQL functions to connect to database
        connection = get_db_connection()
        cursor = connection.cursor()

        #
        try: 
            cursor.execute('INSERT INTO users (username, password) VALUES (?,?)',
            (username, hashed_password))
            connection.commit

        finally:
            connection.close()

        return redirect(url_for('login'))

    return render_template('register.html')



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

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user_id from session
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('index'))

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
