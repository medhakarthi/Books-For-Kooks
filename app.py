from flask import Flask, render_template, request,session,redirect
from flask_session import Session
from cs50 import SQL

app=Flask(__name__)

app.config["SESSION PAYMENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)

db=SQL("sqlite:///books.db")

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect ("/login")
    return render_template("index.html")


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        if not username:
            return ("enter username")
        if not password:
            return ("enter password")

        user=db.execute("SELECT * FROM users WHERE username = ? AND password = ?",username,password)
        if not user:
            return ("invalid username or password")
        else:
            session["user_id"] = user[0]["id"]
            return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")

        if not username:
            return ("missing username")
        if not password:
            return ("missing password")

        db.execute("INSERT INTO users (username,password) VALUES(?,?)",username,password)
        return redirect("/login")
    else:
        return render_template("signup.html")



@app.route("/bookinfo",methods=["GET","POST"])
def bookinfo():
    if "user_id" not in session:
        return redirect("/login")

    if request.method=="POST":
        title=request.form.get("title")
        author=request.form.get("author")

        if not title:
            return ("missing title")
        if not author:
            return ("missing author")
        author="['" + author + "']"

        rows=db.execute("SELECT description,title,authors FROM bookdetails WHERE title=? AND authors=?",title,author)
        return render_template("bookinforesults.html",rows=rows)
    else:
        return render_template("bookinfo.html")


@app.route("/reviews",methods=["GET","POST"])
def reviews():
    if "user_id" not in session:
        return redirect("/login")
    if request.method=="POST":
        title=request.form.get("title")
        author=request.form.get("author")

        if not title:
            return ("missing title")
        if not author:
            return ("missing author")
        author="['" + author + "']"

        rows=db.execute("SELECT profileName, [review/score], [review/text] FROM bookratings WHERE Title IN (SELECT Title FROM bookdetails WHERE authors=? AND Title=?) LIMIT 10", author,title)
        return render_template("reviewsresults.html",rows=rows)

    else:
        return render_template("reviews.html")

@app.route("/addshelf",methods=["GET","POST"])
def addshelf():
    if "user_id" not in session:
        return redirect("/login")

    if request.method=="POST":
        title=request.form.get("title")
        author=request.form.get("author")
        status=request.form.get("read")
        if not title or not author or not status:
            return ("invalid input")
        user_id=session["user_id"]
        db.execute("INSERT INTO bookshelf (user_id,title,author,status) VALUES(?,?,?,?)",user_id,title,author,status)
        return render_template("addshelf.html")
    else:
        return render_template("addshelf.html")

@app.route("/bookshelf")
def bookshelf():
    if "user_id" not in session:
        return redirect("/login")
    user_id=session["user_id"]

    rows=db.execute("SELECT title,author,status FROM bookshelf WHERE user_id==?",user_id)
    return render_template("bookshelf.html",rows=rows)