@app.errorhandler(404)
def pnf(e):
    template = '''<html>
    <body>
    <h3>%s</h3>
    </body>
    </html>
    ''' % request.url

    return render_template_string(template), 404
