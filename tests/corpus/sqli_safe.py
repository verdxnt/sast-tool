@app.route('/search', methods=['POST'])
def search():
    search_term = request.json['search']
    return db.engine.execute(text("SELECT * FROM customer WHERE username = :name"), {"name": search_term})
