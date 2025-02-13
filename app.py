from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = 'database/petadoption.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Enables name-based access to columns
    return conn

@app.route('/')
def index():
    """Homepage: List all available pets."""
    conn = get_db_connection()
    pets = conn.execute('SELECT * FROM pets').fetchall()
    conn.close()
    return render_template('index.html', pets=pets)

@app.route('/pet/<int:pet_id>')
def pet_detail(pet_id):
    """Display details for a specific pet."""
    conn = get_db_connection()
    pet = conn.execute('SELECT * FROM pets WHERE id = ?', (pet_id,)).fetchone()
    conn.close()
    if pet is None:
        return 'Pet not found!', 404
    return render_template('pet_detail.html', pet=pet)

@app.route('/adopt/<int:pet_id>', methods=['GET', 'POST'])
def adopt_pet(pet_id):
    """Adoption page: Show form and process adoption requests."""
    if request.method == 'POST':
        adopter_name = request.form['name']
        adopter_email = request.form['email']
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO adoption_requests (pet_id, adopter_name, adopter_email) VALUES (?, ?, ?)',
            (pet_id, adopter_name, adopter_email)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        return render_template('adopt.html', pet_id=pet_id)

if __name__ == '__main__':
    app.run(debug=True)
