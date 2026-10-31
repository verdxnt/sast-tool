@app.route("/yaml_hammer", methods=['POST'])
def yaml_hammer():
    f = request.files['file']
    file_path = os.getcwd() + '/Files/' + secure_filename(f.filename)
    f.save(file_path)

    with open(file_path, 'r') as yfile:
        y = yfile.read()

    ydata = yaml.load(y)
    return render_template('view.html', name=json.dumps(ydata))
