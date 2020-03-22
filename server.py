from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
import re
from flask_bcrypt import Bcrypt        
from datetime import datetime

app = Flask(__name__)
app.secret_key = "keep it secret"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
bcrypt = Bcrypt(app)


@app.route('/')
def new_user():
    return render_template('index.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    print(request.form)
    is_valid = True
    # First Name
    if len(request.form['fname']) < 1:
    	is_valid = False
    	flash("Please enter a first name")
    elif not str.isalnum(request.form['fname']):
        is_valid = False
        flash("Please enter first name with letters only")
    # Last Name
    if len(request.form['lname']) < 1:
    	is_valid = False
    	flash("Please enter a last name")
    elif not str.isalnum(request.form['fname']):
        is_valid = False
        flash("Please enter last name with letters only")
    # Email
    if len(request.form['email']) < 1:
        is_valid = False
        flash("Please enter an email address")
    elif not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Please enter a valid email address")
    else:
        mysql = connectToMySQL('dojo_tweets_db')
        query = 'SELECT * FROM users WHERE email = %(em)s;'
        data = {
            'em':request.form['email']
        }
        user = mysql.query_db(query,data)
        if user:
            is_valid = False
            flash('Email aready in use')


    #Password
    if len(request.form['pword']) < 5:
    	is_valid = False
    	flash("Password should be at least 5 characters")
    elif request.form['passconf'] != request.form['pword']:
        is_valid = False
        flash("Passwords do not match")
    
    if is_valid:
        pw_hash = bcrypt.generate_password_hash(request.form['pword'])
        mysql = connectToMySQL("dojo_tweets_db")
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(pass)s, NOW(), NOW());"
        data = {
            "fn": request.form["fname"],
            "ln": request.form["lname"],
            "em": request.form["email"],
            "pass": pw_hash,
        }
        new_user = mysql.query_db(query, data)
        session['user_id'] = new_user

        mysql = connectToMySQL("dojo_tweets_db")
        query = "INSERT INTO follows (created_at, updated_at, user_following, user_followed) VALUES (NOW(), NOW(), %(ses)s, %(ses)s)"
        data = {
            'ses': session["user_id"]
        }
        follow = mysql.query_db(query,data)
        return redirect('/dashboard')
    return redirect("/")

@app.route('/user_login', methods=['POST'])
def user_login():
    is_valid = True
        
    if len(request.form['email']) < 1:
        is_valid = False
        flash("Please enter an email address")
    elif not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Please enter a valid email address")
    if len(request.form['pword']) < 1:
    	is_valid = False
    	flash("Please Enter a Valid Password")
    elif request.form['passconf'] != request.form['pword']:
        is_valid = False
        flash("Email and/or password do not match")
    if is_valid:
        mysql = connectToMySQL('dojo_tweets_db')
        query = "SELECT * FROM users WHERE email = %(em)s"
        data = {
            "em": request.form["email"]
        }
        user = mysql.query_db(query, data)
        if user:
            if bcrypt.check_password_hash(user[0]['password'], request.form['pword']):
                session['user_id'] = user[0]['id']
                return redirect('/dashboard')
            else:
                flash("Email and/or password do not match")
        else:
            flash("Email and/or password do not match")
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    elif session['user_id'] < 1:
        return redirect('/')
    print(f"user in session is {session['user_id']}")
    
    mysql = connectToMySQL('dojo_tweets_db')
    query = "SELECT * FROM users WHERE users.id = %(ses)s;"
    data = {'ses': session["user_id"]}
    logged_user = mysql.query_db(query, data)
    
    mysql = connectToMySQL('dojo_tweets_db')
    query = "SELECT * FROM follows WHERE user_following = %(ses)s;"
    data = {'ses': session["user_id"]}
    following = mysql.query_db(query, data)
    print('-------------------------------------------')

    if following:
        mysql = connectToMySQL('dojo_tweets_db')
        query = "SELECT * FROM tweets JOIN users ON users.id = tweets.user_id JOIN follows ON follows.user_followed = users.id WHERE follows.user_following = %(id)s ORDER BY tweets.created_at DESC;"
        data = {'id': session['user_id']}
        tweets = mysql.query_db(query, data)
        print(f"tweets is:{tweets}")
        print('-------------------------------------------')

        for tweet in tweets:
            time_since_posted = datetime.now() - tweet['created_at']
            days = time_since_posted.days
            hours = time_since_posted.seconds//3600 
            minutes = (time_since_posted.seconds//60)%60
            
            tweet['time_since_posted'] = (days, hours, minutes)

        mysql = connectToMySQL('dojo_tweets_db')
        query = "SELECT * FROM likes WHERE user_id = %(id)s;"
        data = {'id': session['user_id']}
        liked_tweet_ids = [like_obj['tweet_id'] for like_obj in mysql.query_db(query,data)]
        print(f"likes is:{liked_tweet_ids}")
        print('-------------------------------------------')
    
        return render_template("dashboard.html", user = logged_user, tweets = tweets, liked_tweet_ids=liked_tweet_ids)

    return render_template("dashboard.html", user = logged_user, tweets = [])
    
@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')

@app.route('/tweets/create', methods=['POST'])
def post_tweet():
    if 'user_id' not in session:
        return redirect('/')
    elif session['user_id'] < 1:
        return redirect('/')

    is_valid = True
    if len(request.form['tweet']) > 255:
        is_valid = False
        flash('Post must be less than 255 characters and spaces')
    if is_valid:
        mysql = connectToMySQL('dojo_tweets_db')
        query = "INSERT INTO tweets (content, created_at, updated_at, user_id) VALUE (%(tw)s, NOW(), NOW(), %(ses)s);"
        data = {
            'ses': session["user_id"],
            'tw': request.form['tweet']
        }
        tweet = mysql.query_db(query, data)
    return redirect('/dashboard')

@app.route('/tweets/<tweet_id>/add_like')
def like_tweet(tweet_id):
    if 'user_id' not in session:
        return redirect('/')
    elif session['user_id'] < 1:
        return redirect('/')
    print(tweet_id)
    mysql = connectToMySQL('dojo_tweets_db')
    query = "INSERT INTO likes (created_at, updated_at, user_id, tweet_id) VALUE (NOW(), NOW(), %(ses)s, %(tid)s);"
    data = {
        'ses': session["user_id"],
        'tid': tweet_id
    }
    user = mysql.query_db(query, data)
    return redirect('/dashboard')

@app.route('/tweets/<tweet_id>/unlike')
def unlike_tweet(tweet_id):
    if 'user_id' not in session:
        return redirect('/')
    elif session['user_id'] < 1:
        return redirect('/')
    print(tweet_id)
    mysql = connectToMySQL('dojo_tweets_db')
    query = "DELETE FROM likes WHERE tweet_id = %(tid)s;"
    data = {
        'tid': tweet_id
    }
    user = mysql.query_db(query, data)
    return redirect('/dashboard')

@app.route('/tweets/<tweet_id>/delete', methods=["POST"])
def delete_tweet(tweet_id):
    if 'user_id' not in session:
        return redirect('/')
    elif session['user_id'] < 1:
        return redirect('/')

    mysql = connectToMySQL("dojo_tweets_db")
    query = "DELETE likes FROM tweets JOIN likes ON tweets.id = likes.tweet_id WHERE tweets.id = %(tid)s;"
    data = {
        "tid": tweet_id
    }
    delete_likes = mysql.query_db(query,data)
    
    mysql = connectToMySQL("dojo_tweets_db")
    query = "DELETE FROM tweets WHERE tweets.id = %(tid)s;"
    data = {
        "tid": tweet_id
    }
    delete_tweet = mysql.query_db(query,data)
    return redirect('/dashboard')

@app.route('/tweets/<tweet_id>/edit')
def edit_tweet(tweet_id):
    if 'user_id' not in session:
        return redirect('/')
    elif session['user_id'] < 1:
        return redirect('/')
    
    mysql = connectToMySQL("dojo_tweets_db")
    query = "SELECT * FROM tweets WHERE id = %(tid)s;"
    data = {
        "tid": tweet_id
    }
    edit_tweet = mysql.query_db(query,data)
    session['tweet_id'] = tweet_id
    return render_template('edit_tweet.html', tweets = edit_tweet)

@app.route('/tweets/<tweet_id>/update_tweet', methods=["POST"])
def update_tweet(tweet_id):
    if 'user_id' not in session:
        return redirect('/')
    elif session['user_id'] < 1:
        return redirect('/')
    
    print(tweet_id)
    is_valid = True
    if len(request.form['tweet']) > 255:
        is_valid = False
        flash('Post must be less than 255 characters and spaces')
    if is_valid:
        mysql = connectToMySQL("dojo_tweets_db")
        query = "UPDATE tweets SET content= %(tw)s, updated_at = NOW() WHERE id = %(tid)s;"
        data = {
            "tid": tweet_id,
            "tw": request.form['tweet']
        }
        edit_tweet = mysql.query_db(query,data)
        return redirect('/dashboard')
    return redirect(f"/tweets/{tweet_id}/edit")

@app.route('/users')
def show_users():
    if 'user_id' not in session:
        return redirect('/')
    elif session['user_id'] < 1:
        return redirect('/')
    
    mysql = connectToMySQL("dojo_tweets_db")
    query = "SELECT * FROM users WHERE id != %(ses)s ORDER BY first_name;"
    data = {'ses': session["user_id"]}
    all_users = mysql.query_db(query, data)
    print(all_users)
    
    print(session['user_id'])
    
    mysql = connectToMySQL("dojo_tweets_db")
    query = "SELECT * FROM users WHERE id = %(tid)s;"
    data = {
        "tid": session["user_id"]
    }
    this_user = mysql.query_db(query,data)
    print (this_user)

    mysql = connectToMySQL('dojo_tweets_db')
    query = "SELECT * FROM follows WHERE user_following = %(id)s;"
    data = {'id': session['user_id']}
    already_followed = [follow_obj['user_followed'] for follow_obj in mysql.query_db(query,data)]
    print(f"follows is:{already_followed}")
    print('-------------------------------------------')
    
    
    return render_template('users.html', users = all_users, user = this_user, already_followed=already_followed)

@app.route('/follow/<this_user>')
def follow_user(this_user):
    if 'user_id' not in session:
        return redirect('/')
    elif session['user_id'] < 1:
        return redirect('/')
    
    print(this_user)
    print(session["user_id"])
    mysql = connectToMySQL("dojo_tweets_db")
    query = "INSERT INTO follows (created_at, updated_at, user_following, user_followed) VALUES (NOW(), NOW(), %(ses)s, %(fid)s)"
    data = {
        "fid": this_user,
        'ses': session["user_id"]
    }
    follow = mysql.query_db(query,data)
    return redirect('/users')

@app.route('/unfollow/<this_user>')
def unfollow_user(this_user):
    if 'user_id' not in session:
        return redirect('/')
    print(this_user)
    print(session["user_id"])
    mysql = connectToMySQL("dojo_tweets_db")
    query = "DELETE FROM follows WHERE user_followed = %(fid)s and user_following = %(ses)s;"
    data = {
        "fid": this_user,
        'ses': session["user_id"]
    }
    follow = mysql.query_db(query,data)
    return redirect('/users')

if __name__ == "__main__":
    app.run(debug=True)