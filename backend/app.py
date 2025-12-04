
from flask import Flask, request, jsonify, g, send_from_directory
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "movies.db")

app = Flask(__name__, static_folder='../frontend', static_url_path='/')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    if not os.path.exists(DB_PATH):
        db = sqlite3.connect(DB_PATH)
        c = db.cursor()
        c.execute("CREATE TABLE movies (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, duration INTEGER, description TEXT)")
        c.execute("CREATE TABLE shows (id INTEGER PRIMARY KEY AUTOINCREMENT, movie_id INTEGER, show_time TEXT, total_seats INTEGER, booked_seats INTEGER DEFAULT 0)")
        c.execute("INSERT INTO movies (title, duration, description) VALUES ('DevOps Saga',120,'A DevOps thriller')")
        c.execute("INSERT INTO movies (title, duration, description) VALUES ('Cloud Adventures',95,'Comedy in cloud')")
        c.execute("INSERT INTO shows (movie_id, show_time, total_seats) VALUES (1,'2025-12-11 18:00',30)")
        c.execute("INSERT INTO shows (movie_id, show_time, total_seats) VALUES (1,'2025-12-11 21:00',30)")
        c.execute("INSERT INTO shows (movie_id, show_time, total_seats) VALUES (2,'2025-12-12 17:00',25)")
        db.commit()
        db.close()

@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/movies')
def movies():
    db = get_db()
    rows = db.execute("SELECT * FROM movies").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/shows/<int:movie_id>')
def shows(movie_id):
    db = get_db()
    rows = db.execute("SELECT * FROM shows WHERE movie_id=?", (movie_id,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/book', methods=['POST'])
def book():
    data = request.json
    show_id = data.get("show_id")
    seats = data.get("seats", 1)
    db = get_db()
    row = db.execute("SELECT total_seats, booked_seats FROM shows WHERE id=?", (show_id,)).fetchone()
    if not row:
        return jsonify({"error": "Show not found"}), 404
    total, booked = row
    if booked + seats > total:
        return jsonify({"error": "Not enough seats"}), 400
    db.execute("UPDATE shows SET booked_seats = booked_seats + ? WHERE id=?", (seats, show_id))
    db.commit()
    return jsonify({"message": "Booking success", "booking_id": f"BK-{show_id}-{booked+seats}"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=3000)
