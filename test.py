from flask import Flask, render_template
from pytrips.ontology import get_ontology as ont


from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class WordLookup(FlaskForm):
    name = StringField('name', validators=[DataRequired()])

app = Flask(__name__, template_folder="./templates")
app.secret_key = b"thisisarandomsecretkey"

@app.route("/tree/<string:t>")
def tree(t):
    node = ont()[t]
    print("node", node)
    if node:
        return "<html><pre>{}</pre></html>".format(node.subtree_string())
    return "{} not found".format(t)

@app.route("/word", methods=("GET", "POST"))
def word():
    form = WordLookup()
    if form.validate_on_submit():
        path = ont().get_word_graph(form.name.data).graph()
        return render_template("page.html", svg=path.pipe().decode().strip(), form=form)
    return render_template("page.html", svg="", form=form)
