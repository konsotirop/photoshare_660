######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Mona Jalal (jalal@bu.edu), Baichuan Zhou (baichuan@bu.edu) and Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
import datetime

# for image uploading
# from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'shamir'  # Change this!

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'OreoCooks12'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
# below changed from 'localhost'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email FROM USERS")
users = cursor.fetchall()


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM USERS")
    return cursor.fetchall()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    print(users)
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()

    cursor.execute("SELECT password FROM USERS WHERE email = email")
    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
    # The request method is POST (page is receiving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    # check if email is registered
    query = "SELECT password from USERS WHERE email ='" + email +"'"
    if cursor.execute(query):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user
            return flask.redirect(flask.url_for('protected'))  # protected is a function defined in this file

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"


@app.route('/logout')
def logout():
    flask_login.logout_user()

    return render_template('hello.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress=True)


@app.route("/register_fail", methods=['GET'])
def re_register():
    return render_template('register.html', supress=False)


@app.route("/register", methods=['POST'])
def register_user():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        dob = request.form.get('dob')
    except:
        print(
            "couldn't find all tokens")
        # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    try:
        gender = request.form.get('gender')
    except:
            gender = None
    try:        
        hometown = request.form.get('hometown')
    except:
        hometown = None
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        cursor.execute("INSERT INTO USERS (email, password, gender, dob, hometown, fname, lname) "
                       "VALUES (%s , %s, %s, %s, %s, %s, %s)",
                       (email, password, gender, dob, hometown, fname, lname))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('hello.html', name=email, message='Account Created!')
    else:
        print("User is not unique")
        return flask.redirect(flask.url_for('re_register'))



@app.route("/addfriends", methods=['POST'])
def addfriends():
    return


def getUserNameFromEmail(email):
   cursor = conn.cursor()
   query = "SELECT FNAME, LNAME FROM USERS WHERE email = '"+ email +"'"
   cursor.execute( query )
   data = cursor.fetchall()
   fname = str(data[0][0])
   lname = str(data[0][1])
   return fname, lname


@app.route('/by_tag', methods=['GET'])
def browse_by_tag(uid, tag):
    # 2nd elem in each tuple is pid
    pids = set([p[1] for p in getUsersPhotos(uid)])

    # find photos in pids with desired tag
    cursor = conn.cursor()

    # TODO: does MySQL support python set 'in' syntax?
    query = 'SELECT pid FROM ASSOCIATE WHERE hashtag = %s AND pid in %s', (tag, pids)

    cursor.execute(query)

    data = cursor.fetchall()

    #TODO: return HTML template that takes data as a parameter


def getUsersPhotos(uid):
    cursor = conn.cursor()

    cursor.execute("SELECT img_data, pid, caption FROM PHOTO WHERE uid = '" + str(uid) + "'")
    return cursor.fetchall()


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    query = "SELECT uid  FROM USERS WHERE email ='"+ email +"'"
    cursor.execute(query)
    return cursor.fetchone()[0]


def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    query = "SELECT email FROM USERS WHERE email = '"+ email +"'"
    print(query)
    if cursor.execute( query) :
        # this means there are greater than zero entries with that email
        return False
    else:
        return True


# end login code

def recommend_user():
    current_user = flask_login.current_user.id
    CUID = getUserIdFromEmail(current_user)
    try:
        uemail = request.form.get('user_mail')
    except:
       print(
             "couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)
       return flask.redirect(flask.url_for('protected'))
    query = "SELECT U.FNAME, U.LNAME, U.EMAIL, COUNT(*) AS CF " \
            "FROM USERS AS U, FRIENDSHIP AS F1, FRIENDSHIP AS F2 " \
            "WHERE "+str(CUID)+\
                "=F1.UID1 AND F1.UID2=F2.UID1 AND F2.UID2<>"+str(CUID)+" AND F2.UID2=U.UID AND F1.UID2<>F2.UID2 " \
            "GROUP BY U.UID ORDER BY CF DESC"

    print(query)
    cursor = conn.cursor()
    cursor.execute(query)
    data=cursor.fetchall()
    return data

@app.route('/profile', methods=['GET'])
@flask_login.login_required
def protected( not_found=0, usersList = None ):
    userid = getUserIdFromEmail(flask_login.current_user.id)
    print("***{}***".format(flask_login.current_user.id))
    print("***{}***".format(str(userid)))
    cursor = conn.cursor()
    #albums
    cursor.execute("SELECT A_NAME, AID FROM ALBUM WHERE UID = '" + str(userid) + "'")
    print(str(userid))
    albums = cursor.fetchall()
    print(albums)
    # search
    query = "SELECT U.FNAME, U.LNAME, U.EMAIL FROM FRIENDSHIP AS F, USERS AS U WHERE F.UID1=" \
            + str(userid)+ " AND F.UID2=U.UID"
    friendsList = ()
    if cursor.execute(query):
        friendsList = cursor.fetchall()
        print("Friends: {}".format(friendsList))

    firstname, lastname = getUserNameFromEmail(flask_login.current_user.id)
    recommendations=recommend_user()

    return render_template('profile.html', fname=firstname, lname=lastname, nf=not_found, users=usersList,\
                           friends=friendsList, recommendations=recommendations, albums= albums )


@app.route("/profile", methods=['POST'])
@flask_login.login_required
def search_User():
    current_user = flask_login.current_user.id
    try:
        uemail = request.form.get('userSearch')
    except:
        print(
            "couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('protected'))
    cursor = conn.cursor()
    notSelf = " AND EMAIL <> '"+current_user+"'"
    query = "SELECT fname, lname, email FROM USERS WHERE email LIKE '"+ uemail +"%'"+notSelf
    print(query)
    if ( cursor.execute(query) ):
        data = cursor.fetchall()
        return user_results( data )
    else:
        return protected( not_found=1 )


def user_results(usersList):

    return protected(0, usersList)


@app.route('/profile/1', methods=['POST'])
@flask_login.login_required
def visit_user():
    print("mpika")
    current_user = flask_login.current_user.id
    try:
        uemail = request.form.get('user_mail')
    except:
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('protected'))
    print( current_user, uemail )
    firstname, lastname = getUserNameFromEmail(uemail)
    already=0
    cuid = getUserIdFromEmail(current_user)
    ouid = getUserIdFromEmail(uemail)
    query = "SELECT * FROM FRIENDSHIP WHERE UID1="+str(cuid)+" AND UID2="+str(ouid)
    if cursor.execute(query):
        already=1
    query = "SELECT A_NAME, AID FROM ALBUM WHERE UID =" + str(ouid)
    cursor.execute(query)
    albums = cursor.fetchall()
    print(query)
    return render_template('otherProfile.html',
                           fname=firstname, lname=lastname, otherEmail=uemail,
                           already=already, message="(S)he is a friend of you", albums=albums)


@app.route('/user_album', methods=['POST'])
@flask_login.login_required
def view_album():
    try:
        cur_aid = request.form.get('album_id')
    except:
        print("Could find this album: " + str(cur_aid))
        return flask.redirect(flask.url_for('protected'))

    query = "SELECT * FROM PHOTO WHERE AID=" + str(cur_aid)
    cursor.execute(query)
    photos = cursor.fetchall()

    return render_template('view_album.html', photos=photos, aid=cur_aid)


@app.route('/other_user_album', methods=['POST'])
def view_other_album():
    try:
        cur_aid = request.form.get('album_id')
    except:
        print("Could find this album: " + str(cur_aid))
        return flask.redirect(flask.url_for('protected'))

    query = "SELECT * FROM PHOTO WHERE AID=" + str(cur_aid)
    cursor.execute(query)
    photos = cursor.fetchall()

    return render_template('view_other_album.html', photos=photos, aid=cur_aid)


# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        parent_album = request.form.get('album_name')
        print(caption)
        photo_data = base64.standard_b64encode(imgfile.read())
        cursor = conn.cursor()
        aid_query = \
            cursor.execute("SELECT AID FROM ALBUM WHERE A_NAME = %s AND UID = %s",
                           (parent_album, uid))

        cursor.execute("INSERT INTO PHOTO (IMG_DATA, UID, CAPTION, AID) VALUES (%s, %s, %s, %s)",
                       (photo_data, uid, caption, aid_query))
        conn.commit()
        return render_template('hello.html',
							   name=flask_login.current_user.id,
							   message='Photo uploaded!',
                               photos=getUsersPhotos(uid))
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('upload.html')


@app.route('/create_album', methods=['GET','POST'])
@flask_login.login_required
def create_album():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        print(str(uid))
        album_name = request.form.get('Name')
        date_time = datetime.datetime.now()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ALBUM (A_NAME, UID, DOC) VALUES (%s, %s, %s)", (album_name, uid, date_time))
        conn.commit()
        return flask.redirect(flask.url_for('protected'))
    else:
        return render_template('create_album.html')

@app.route('/friendship', methods=['POST'])
@flask_login.login_required
def friendship():
    try:
        uemail = request.form.get('friend')
        firstname, lastname = getUserNameFromEmail(uemail)
        other = getUserIdFromEmail(uemail)
        current = getUserIdFromEmail(flask_login.current_user.id)
        print(other, current)
        cursor.execute("INSERT INTO FRIENDSHIP ( UID1, UID2 ) VALUES (%s, %s)", (current, other))
        conn.commit()
        return render_template('otherProfile.html', fname=firstname, lname=lastname, otherEmail=uemail, already=1,
                               message="Added to your friends' list!")
    except:
        print("couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)


# default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welcome to Photoshare')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
