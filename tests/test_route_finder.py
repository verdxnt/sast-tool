import ast
from pathlib import Path

from route_finder import find_routes

CORPUS = Path(__file__).parent / "corpus"


def parse(filename):
    return ast.parse((CORPUS / filename).read_text(encoding="utf-8"))


def test_finds_single_route():
    routes = find_routes(parse("sqli_vulnerable.py"))

    assert len(routes) == 1
    path, node = routes[0]
    assert path == "/search"
    assert node.name == "search"


def test_stacked_routes_share_one_function():
    source = '''
@app.route("/dashboard")
@app.route("/home")
def dashboard():
    pass
'''
    routes = find_routes(ast.parse(source))

    assert len(routes) == 2
    assert routes[0][0] == "/dashboard"     # first entry's path
    assert routes[1][0] == "/home"     # second entry's path
    assert routes[0][1] is routes[1][1]   # both entries hold the same function node
