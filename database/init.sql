-- Users table (for future use)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

-- Pets table (for manually added pets)
CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    breed TEXT,
    age INTEGER,
    description TEXT,
    image_url TEXT
);

-- Adoption Requests table (for tracking adoptions)
CREATE TABLE IF NOT EXISTS adoption_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER NOT NULL,
    adopter_name TEXT NOT NULL,
    adopter_email TEXT NOT NULL,
    request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES pets(id)
);

-- AI-Generated Things table (For AI-created creatures)
CREATE TABLE IF NOT EXISTS things (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    species TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    description TEXT NOT NULL
);

-- Table to store AI-generated images for each Thing
CREATE TABLE IF NOT EXISTS thing_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thing_id INTEGER NOT NULL,
    image_url TEXT NOT NULL,
    FOREIGN KEY (thing_id) REFERENCES things(id)
);
