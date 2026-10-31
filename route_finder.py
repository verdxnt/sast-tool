import ast

ROUTE_DECORATORS = {"route", "errorhandler"}


def find_routes(tree):
    routes = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            if not isinstance(decorator.func, ast.Attribute):
                continue
            if decorator.func.attr not in ROUTE_DECORATORS:
                continue
            if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
                continue
            routes.append((str(decorator.args[0].value), node))
    return routes
