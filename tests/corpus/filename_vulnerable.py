@app.route("/upload", methods=['POST'])
def upload():
    f = request.files['file']
    fname = f.filename
    file_path = os.getcwd() + '/Files/' + fname
    f.save(file_path)
    return "saved", 200
