from flask import Flask, render_template
from pytrips.ontology import get_ontology as ont
from tripscli.parse.web import TripsParser
from tripscli.parse.web.dot import as_dot
from pytrips.nodegraph import type_to_dot


from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class WordLookup(FlaskForm):
    name = StringField('name', validators=[DataRequired()])

class ParseSentence(FlaskForm):
    sentence = StringField('input', validators=[DataRequired()])
    parser = StringField('input', default="http://trips.ihmc.us/parser/cgi/step")

app = Flask(__name__, template_folder="./templates")
app.secret_key = b"thisisarandomsecretkey"

@app.route("/tree/<string:t>")
def tree(t):
    node = ont()[t]
    print("node", node)
    if node:
        return "<html><pre>{}</pre></html>".format(node.subtree_string())
    return "{} not found".format(t)

@app.route("/graph/<string:t>")
def nodegraph(t):
    node=ont()[t]
    if node:
        return render_template("ng.html", svg=type_to_dot(node).pipe().decode().strip())
    return "type %s not found..." % t

@app.route("/word", methods=("GET", "POST"))
def word():
    form = WordLookup()
    if form.validate_on_submit():
        path = ont().get_word_graph(form.name.data, use_stop=False)
        path.ont = ont()
        path = path.graph()
        return render_template("page.html", svg=path.pipe().decode().strip(), form=form)
    return render_template("page.html", svg="", form=form)

@app.route("/parse", methods=("GET", "POST"))
def parse():
    form = ParseSentence()
    if form.validate_on_submit():
        data = TripsParser(url=form.parser.data, debug=False).query(form.sentence.data)
        print(as_dot(data, "sentence", "default").graph(format="dot"))
        return render_template(
            "parse-data.html",
            parse=as_dot(data, "sentence", "default").graph().pipe().decode().strip(),
            form=form
        )
    return render_template("parse.html", form=form)
