@app.route('/search', methods=['POST'])
def search():
    search_term = request.json['search']
    query = "SELECT * FROM customer WHERE username = '%s';" % search_term
    return db.engine.execute(query)
