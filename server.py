"""Movie Ratings."""

from jinja2 import StrictUndefined


from flask_debugtoolbar import DebugToolbarExtension
from flask import (Flask, render_template, redirect, request, flash,
                  session, jsonify)

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    # a = jsonify([1,3])
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/register_form")
def display_register_form():
    """"""

    return render_template("register_form.html")


@app.route("/register", methods=["POST"])
def register():

    username = request.form.get("email")
    password = request.form.get("password")

    if db.session.query(User.email).filter_by(email=username).first():
        flash("Sorry the email has already been registered.")
        return redirect("/register_form")

    else:
        new_user = User(email=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("You are successfully registered!")
        return render_template("homepage.html")


@app.route("/login", methods=["GET"])
def login_input():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    u_username = request.form.get("email")
    u_password = request.form.get("password")
    user_info = User.query.filter_by(email=u_username).first()

    # ser.query(Rating.movie_id, Rating.score).join(Rating).filter(User.email==u_username).all()
    
    if user_info:
        user_id = user_info.user_id
        if user_info.password == u_password:
            flash("Successfully logged in!")
            session["login"] = user_info.email
            return redirect("/users/%s" % user_id)
            

    # if db.session.query(User.email, User.password).filter_by(email=u_username).first():
    #     (d_username, d_password) = db.session.query(User.email, User.password).filter_by(email=u_username).first()
    #     if u_password == d_password:
    #         flash("Successfully logged in!")
    #         session["login"] = d_username
    #         return redirect("/")
        else:
            flash("Wrong Password")
            return render_template("login.html")
    else:
        flash("User not found!")
        return render_template("login.html")



@app.route("/logout", methods=["GET"])
def logout_screen():
    return render_template("logout.html")


@app.route("/logout", methods=["POST"])
def logout():

    if not session.get("login"):
        session.pop("login")

    flash("You have been successfully logged out.")

    return redirect("/")


@app.route("/users/<user_id>")
def show_user_info(user_id):
    """Show users info"""

    u_username = request.form.get("email")
    user_info = User.query.filter_by(email=u_username).first()
    rating_info = user_info.ratings

    return render_template("show_user_info.html", rating_info=rating_info,
                            user_info=user_info)


@app.route("/movies", methods=['GET'])
def movies():

    movie_info = db.session.query(Movie).all()

    return render_template("movies.html", movie_info=movie_info)


@app.route("/movies/<movie_id>", methods=["POST"])
def movie_rated(movie_id):


    added_rating = request.form.get("rate_score")
    print session['login']
    user_id = User.query.filter_by(email=session["login"]).first().user_id


    all_movies_rated_by_user = Rating.query.filter_by(user_id=user_id).all()
    print all_movies_rated_by_user

    flash("Your rating has been updated.")

    return redirect("/movies")


@app.route("/movies/<movie_id>")
def show_movies(movie_id):
    """Show movie rating info"""

    show_movie_ratings = Rating.query.filter_by(movie_id=movie_id).all()
    title_of_movie = Movie.query.filter_by(movie_id=movie_id).first().title

    return render_template("show_movie_info.html", 
                           show_movie_ratings=show_movie_ratings,
                           title_of_movie=title_of_movie, movie_id=movie_id)






if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


  
    app.run(port=5000, host='0.0.0.0')
