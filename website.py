from flask import Flask,render_template,request,redirect,url_for,session
from datetime import  datetime
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail
import os



with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key=os.urandom(24)
app.config.update(
    MAIL_SERVER="smpt.gamil.com",
    MAIL_PORT="465",
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params["USER-ID"],
    MAIL_PASSWORD=params["USER-PASS"])
mail=Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)


class contacts(db.Model):
    __tablename__ = 'contacts'
    sno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), nullable=False)
    Number = db.Column(db.String(12), nullable=False)
    Massage = db.Column(db.String(500), nullable=False)
    Date = db.Column(db.String(120), nullable=True)
    Email = db.Column(db.String(50),  nullable=False)

class posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(30), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    Date = db.Column(db.String(120), nullable=True)
    img_file = db.Column(db.String(50),  nullable=False)

@app.route("/signin", methods=["GET","POST"])
def dashboard():
    if ('user' in session and session['user']==params["admin_user"]):
        return render_template("adminpanel.html",params=params)
    if request.method=="POST":
        username=request.form.get("uname")
        userpass=request.form.get("pass")
        if username==params["admin_user"] and userpass==params["admin_pass"]:
            session["user"]=username
            return render_template("adminpanel.html",params=params)

    return render_template("dashboard.html", params=params)
@app.route("/blog")
def index():

    return render_template("index.html",params=params)

@app.route("/about")
def about():
    if ('user' in session):
        return render_template("about.html",params=params)

    return redirect(url_for('dashboard'))
@app.route("/contact",methods=["GET","POST"])
def contact():

    if (request.method=="POST"):
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        entry = contacts(Name=name, Number=phone, Massage=message, Date=datetime.now(), Email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New messsage from'+ name,
                              sender=email,
                              recipients=params["USER-ID"],
                              body=message+"\n"+phone
                              )

    return render_template("contact.html", params=params)
@app.route("/post/")
def post_route(post_slug):
    post=posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html",params=params)
if __name__=="__main__":
    app.run(debug=True)
