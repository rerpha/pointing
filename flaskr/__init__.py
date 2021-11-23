import os
from statistics import mean
from flask import Flask, request


class Points:
    priorities = [1, 2, 3]
    points = [1, 2, 3, 5, 8, 13, 20, 40]
    is_points = True


current_points = Points()


def _generate_html(point_buttons, votes):
    return f"""
<html>
    <head>
        <title>Pointing</title>
    </head>
    <body>
    <ul style="list-style: none; margin: 0; padding: 0;>
        { point_buttons }
    </ul>
    <br>
    <ul style="list-style: none; margin: 10; padding: 10;">
        <li style="display: inline"><button onClick="location.reload()">Show Votes</button><li>
        <li style="display: inline"><button onClick="reset()">Reset Votes</button><li>
        <li style="display: inline"><button onClick="change_points()">Switch voting type</button><li>
    </ul>
    
    <h1> votes: {votes} </h1>
    <h1> Average vote: {mean(votes) if votes else "" } </h1>
    
    <script>
    
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
      Array.from(document.getElementsByID("point"))
  .forEach(b => b.disabled = true)

    }}
    function reset() {{ 
    var xhr = new XMLHttpRequest();
      xhr.open("GET", "/reset", true);
      xhr.send("");
      sleep(500);
      location.reload();
    }}
    function change_points() {{ 
    var xhr = new XMLHttpRequest();
      xhr.open("GET", "/change_points", true);
      xhr.send("");
      sleep(500);
      location.reload();
    }}
    </script>
    </body>
</html>"""


def _create_point_buttons(items):
    point_buttons = ""
    for item in items:
        point_buttons += f'<li style="display: inline"><button id="point" onClick="send({item})">{item} </button></li>\n'
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

    @app.route("/change_points", methods=["GET"])
    def change_points():
        current_points.is_points = not current_points.is_points
        reset()
        return "200"

    return app
