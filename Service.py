from flask import render_template, request, redirect,session,  url_for
from initdb import app, get_db, insert_db, query_db

@app.route("/")
def youlk():
    return render_template("youlk.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if 'userid' in session:
        flash(u"あなたはすでにログインしています", 'warning')
        return redirect(url_for('profile', userid=session['userid']))
    else:
        if request.method == 'GET':
            return render_template("register.html", session=session)
        elif request.method == 'POST':
            session["gender"]= request.form.get("gender")
            session["name"]= request.form.get("name")
            session["nickname"]= request.form.get("nickname")
            session["age"]= request.form.get("age")
            session["job"]= request.form.get("job")
            session["email"]= request.form.get("email")
            session["telephone_number"]= request.form.get("telephone_number")
            if len(request.form.get("password1")) <=8 or request.form.get("password1" ) != request.form.get("password2"):
                return redirect("/register")
            if re.fullmatch(emailRegEx, session['email']) == None:
                flash(u"そのメールアドレスは登録済みなので登録できません。", 'warning')
                return redirect(url_for("register"))
            else:

                insert_db("INSERT INTO user (gender, name,nickname, age, job,address, email, password) \
                           VALUES(?,?,?,?,?, ?, ?, ?)",
                           (sessin["gender"], session["name"],session["nickname"],session["age"], session["job"],
                           session["address"], session["email"], request.form.get("password1" )))
                user = query_db("SELECT * FROM user WHERE email = ?", (session["email"],), True)
                session['userid'] = user['id']
                return render_template("profile.html", user=user)

@app.route("/profile", methods=["GET", "POST"])
def profile(userid):
    # If not logged in
    if 'userid' not in session:
        flash(u"あなたはまだログインしていません。ログインしてあなたの情報を追加しましょう。", 'warning')
        return redirect(url_for("login_menu"))
    # Check if it's a valid user
    elif int(userid) != session['userid']:
        user = query_db("SELECT * FROM user WHERE id = ?", (int(userid),), True)
        if user == None:
            flash(u"アカウントが存在しません。新規登録してください", 'warning')
            return redirect(url_for('profile', userid=session['userid']))
        else:
            return render_template("profile.html", session=session, user=user)
    else:
        return render_template("profile.html", session=session)

@app.route("/login_menu", methods=["GET","POST"])
def login_menu():
    # If already logged in
    if 'userid' in session:
        flash(u"あなたはすでにログインしています", 'warning')
        return redirect(url_for('profile', userid=session['userid']))
    else:
        if request.method == 'GET':
            return render_template("login_menu.html", session=session)
        elif request.method == 'POST':
            # Store inputs (except password) in session to auto-fill the forms when redirected
            session['email'] = request.form.get("email")
            request.form.get("password1")

            # Confirm user exists, and entered password matches the stored password
            user = query_db("SELECT * FROM user WHERE email = ?", (session['email'],), True)
            if user == None:
                flash(u"メールアドレスまたは、パスワードに誤りがあります。もう一度お試しください。.", 'warning')
                return redirect(url_for("login_menu"))
            elif request.form.get("password1") != user['password1']:
                flash(u"メールアドレスまたは、パスワードに誤りがあります。もう一度お試しください。", 'warning')
                return redirect(url_for("login_menu"))

            # Store user info in session just for convenience
            session['userid'] = user['id']
            session['name']   = user['name']
            session['nickname'] = user['nickname']
            session['age'] = user['age']
            session['job']   = user['job']
            session['email'] = user['email']
            session['telephone_number'] = user['telephone_number']

            flash(u"ようこそ", 'info')
            return redirect(url_for('profile', userid=session['userid']))


@app.route("/logout_menu")
def logout_menu():
    # If not logged in
    if 'userid' not in session:
        flash(u"あなたはまだログインしていません。ログインしてyoulkをみてみましょう", 'warning')
        return redirect(url_for("login_menu"))
    else:
        session.clear()
        flash(u"ログアウトしました。また会う日まで", 'info')
        return redirect(url_for('youlk'))

@app.route("/<int:userid>/edit", methods=["GET", "POST"])
def update(userid):
    # If not logged in
    if 'userid' not in session:
        flash(u"ログインが完了していません。まずはログインしてください。", 'warning')
        return redirect(url_for("login"))
    # Check if it's a valid user
    elif int(userid) != session['userid']:
        flash(u"他書の情報を変更できません。", 'warning')
        return redirect(url_for('profile', userid=session['userid']))
    else:
        if request.method == 'GET':
            return render_template("edit_profile.html", session=session)
        elif request.method == 'POST':
            # Validate email (has to be unique, and has to contain @, followed by .)
            if re.fullmatch(emailRegEx, request.form.get("email")) == None:
                flash(u"Invalid email address. Please try again.", 'warning')
                return redirect(url_for("update", userid=session['userid']))
            else:
                user = query_db("SELECT * FROM user WHERE email = ?", (request.form.get("email"),), True)
                if (user != None) and (user['id'] != session['userid']):
                    flash(u"そのメールアドレスは使用できません。", 'warning')
                    return redirect(url_for("update", userid=session['userid']))

            # Validate password (has to be longer than 8 characters,
            # and has to contain at least one uppercase, lowercase, and digit, respectively)
            # Also, password is NOT stored in session for security purposes
            if re.fullmatch(pwRegEx, request.form.get("password")) == None:
                flash(u"パスワードは８文字以上でお願いします。", 'warning')
                return redirect(url_for("update", userid=session['userid']))

            # Store inputs (except password) in session for convenience
            session['name']   = request.form.get("name")
            session['email']  = request.form.get("email")
            session['gender'] = request.form.get("gender")

            # Update user info in DB only if passed all validations
            modify_db("UPDATE user \
                       SET name=?, email=?, password=?, gender=? \
                       WHERE id=?",
                       (session['name'], session['email'], request.form.get("password"), session['gender'], session['userid']))

            flash(u"編集が完了しました。", 'info')
            return redirect(url_for('profile', userid=session['userid']))

#
# @app.route("/picture", methods=["GET","POST"])
# def picture():
#
#
# @app.route("/talk", methods=["GET","POST"])
# def talk():
#
#
# @app.route("/friend_list", methods=["GET","POST"])
# def friend_list():
#


if __name__ == '__main__':
    app.run()
