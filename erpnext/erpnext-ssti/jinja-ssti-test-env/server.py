from flask import *

app = Flask(__name__)

@app.route("/basic", methods=["GET", "POST"])
def basic():
        output = request.values.get('name')
        output = render_template_string(output)
        return output
@app.route("/hardened", methods=["GET", "POST"])
def hardened():
        output = request.values.get('name')
        if '_' in output:
            output = render_template_string('BLOCKED')
        else:
            output = render_template_string(output)
        return output
@app.route("/hardened_max", methods=["GET", "POST"])
def hardened_max():
        output = request.values.get('name')
        bad = ['.','_','|join',',','mro','base']
        if any(restricted  in output for restricted in bad):
            output = render_template_string('BLOCKED')
        else:
            output = render_template_string(output)
        return output
if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=6080)
