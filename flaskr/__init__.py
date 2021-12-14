import os
from statistics import mean
from flask import Flask, request


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
    """


def _generate_html(point_buttons, votes):
    return f"""
    <!doctype html>
        <html>
            <head>
                <title>Pointing</title>
                <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🐐</text></svg>">
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
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

                    <div class="btn-group" role="group">
                        <button class="btn btn-primary" onClick="location.reload()">Show</button>
                        <button class="btn btn-danger" onClick="reset()">Reset</button>
                    </div>
                    <br><br>
                    <div class="btn-group btn-group-toggle" role="group">
                        <button class="btn btn-primary" onClick="change_points(1)">Points</button>
                        <button class="btn btn-primary" onClick="change_points(0)">Priorities</button>
                    </div>

                </div>
                <script>
                    {SCRIPT}
                </script>
                <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
                <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
            </body>
        </html>
    """


def _create_point_buttons(items):
    point_buttons = ""
    for item in items:
        point_buttons += f'<li style="display: inline"><button class="btn btn-primary btn-sm" name="point" onClick="send({item})">{item} </button></li>\n'
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

    @app.route("/")
    def hello():
        items = (
            current_points.points
            if current_points.is_points
            else current_points.priorities
        )
        return _generate_html(_create_point_buttons(items), votes)

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
