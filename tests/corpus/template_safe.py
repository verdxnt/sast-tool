@app.errorhandler(404)
def pnf(e):
    template = '''<html>
    <body>
    <h3>{{ current_url }}</h3>
    </body>
    </html>
    '''

    return render_template_string(template, current_url=request.url), 404
