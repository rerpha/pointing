import os
from statistics import mean
from flask import Flask, request

CSS_SCRIPTS = """
<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
                <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
"""
CSS_LINKS = """
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🐐</text></svg>">
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
"""
USERS_FILENAME = "users.txt"
ADMIN_CONTROLS = """
<div class="btn-group" role="group" >
                        <button class="btn btn-primary" onClick="location.reload()">Show</button>
                        <button class="btn btn-danger" onClick="reset()">Reset</button>
                    </div>
                    <br><br>
                    <div class="btn-group btn-group-toggle" role="group">
                        <button class="btn btn-primary" onClick="change_points(1)">Points</button>
                        <button class="btn btn-primary" onClick="change_points(0)">Priorities</button>
                    </div>
"""


class Points:
    priorities = [1, 2, 3]
    points = [1, 2, 3, 5, 8, 13, 20, 40]
    is_points = True


current_points = Points()

SCRIPT = """
    function sleep(milliseconds) {{
        const date = Date.now();
        let currentDate = null;
        do {{
            currentDate = Date.now();
        }} while (currentDate - date < milliseconds);
        }}
    function send(point) {{
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/send?point=" + point, true);
        xhr.send("");
        Array.from(document.getElementsByName("point"))
            .forEach(b => b.disabled = true)
    }}
    function reset() {{ 
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "/reset", true);
        xhr.send("");
        sleep_and_reload();
    }}
    function change_points(is_points) {{ 
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/change_points?is_points=" + is_points, true);
        xhr.send("");
        sleep_and_reload();
    }}
    function sleep_and_reload() {{
        sleep(100);
        location.reload();
    }}
    function redir(user) {{
        let url = `/?user=${user}`;
        console.log(user);
        console.log(url);
        window.location.replace(url);
    }}
    """


def _generate_html(point_buttons, votes, user, is_admin=False):
    return f"""
    <!doctype html>
        <html>
            <head>
                <title>Pointing</title>
                { CSS_LINKS }
            </head>
            <style>
            .content {{
                max-width: 300px;
                margin: 0 auto;
                justify-content: center;
                align-items: center;
            }}
            </style>
            <body>
                <div class="container-fluid content">

                    <h1>Pointing 🐐</h1>
                    <ul style="list-style: none; margin: 0; padding: 0;>
                        { point_buttons }
                    </ul>

                    <div>
                    <h2> Votes: {votes} </h2>
                    <h2> Avg vote: {mean(votes) if votes else 0 } </h2>
                    <h2> Num votes: {len(votes)} </h2>
                    </div>

                    <h2> User: {user} </h2>

                    {ADMIN_CONTROLS if is_admin else ""}

                </div>
                <script>
                    {SCRIPT}
                </script>
                {CSS_SCRIPTS}
            </body>
        </html>
    """


def _generate_html_pickuser(user_buttons):
    return f"""
    <!doctype html>
        <html>
            <head>
                <title>Pointing</title>
                { CSS_LINKS }
            </head>
            <style>
            .content {{
                max-width: 300px;
                margin: 0 auto;
                justify-content: center;
                align-items: center;
            }}
            </style>
            <body>
                <div class="container-fluid content">

                    <h1>Pick user 🐐</h1>
                    <ul style="list-style: none; margin: 0; padding: 0;>
                        { user_buttons }
                    </ul>

                </div>
                <script>
                    {SCRIPT}
                </script>
                {CSS_SCRIPTS}
            </body>
        </html>
    """


def _create_point_buttons(items, js_func="send"):
    point_buttons = ""
    for item in items:
        point_buttons += f'<li style="display: inline"><button class="btn btn-primary btn-sm" name="point" onClick="{js_func}({item})">{item} </button></li>\n'
    return point_buttons


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    votes = []
    user_list = []
    try:
        with open(USERS_FILENAME, "r") as users_file:
            user_list = users_file.read().split(" ")
    except OSError:
        print("error opening users list")

    @app.route("/admin")
    def admin():
        return main(True)

    @app.route("/")
    def main(is_admin=False):
        user = request.args.get("user")
        if user is None:
            return "not signed in"
        items = (
            current_points.points
            if current_points.is_points
            else current_points.priorities
        )
        return _generate_html(_create_point_buttons(items), votes, user, is_admin)

    @app.route("/pickuser")
    def pickuser():
        return _generate_html_pickuser(
            _create_point_buttons(["'" + user + "'" for user in user_list], js_func="redir")
        )

    @app.route("/send", methods=["POST"])
    def send():
        point = int(request.args.get("point"))
        votes.append(point)
        return "200"

    @app.route("/reset", methods=["GET"])
    def reset():
        votes.clear()
        return "200"

    @app.route("/change_points", methods=["POST"])
    def change_to_points():
        is_points = bool(int(request.args.get("is_points")))
        current_points.is_points = is_points
        reset()
        return "200"

    return app
