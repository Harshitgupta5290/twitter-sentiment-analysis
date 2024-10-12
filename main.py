from flask import Flask, render_template, request, redirect, session, flash, url_for
from models import get_db_connection, create_tables
from sentiments import second
import os
import sqlite3
from forms import LoginForm, RegisterForm, ForgotPasswordForm
from datetime import timedelta


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.register_blueprint(second)

# Create the necessary tables if they don't exist
create_tables()

@app.route('/')
def login():
    return redirect(url_for('login_validation'))


@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('inner-pages/index.html')
    else:
        return redirect('/')

    
# Define the login route and logic
@app.route('/login', methods=['GET', 'POST'])
def login_validation():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember_me = form.remember.data

        # Database query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            if remember_me:
                session.permanent = True 
                app.permanent_session_lifetime = timedelta(days=30)
            else:
                session.permanent = False

            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)    


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        remember_me = form.remember_me.data

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Insert the new user with the remember_me value
            cursor.execute(
                "INSERT INTO users (name, email, password, remember_me) VALUES (?, ?, ?, ?)", 
                (name, email, password, remember_me)
            )
            conn.commit()

            # Retrieve the user to store their ID in the session
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            myuser = cursor.fetchone()
            session['user_id'] = myuser['id']

            flash('Registration successful!')
            return redirect(url_for('home'))
        
        except sqlite3.IntegrityError:
            # Handle the error if the email is already in use
            flash('Email already registered. Please use a different email.', 'error')
            return redirect(url_for('register'))
        finally:
            conn.close()
    
    return render_template('register.html', form=form)


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        new_password = form.new_password.data

        # Logic to check if the email exists in the database and update the password
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user:
            # Update the user's password in the database
            cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
            conn.commit()
            flash('Your password has been successfully updated!')
            return redirect(url_for('login'))
        else:
            flash('This email is not registered. Please check and try again.', 'error')

        conn.close()

    return render_template('forgot_password.html', form=form)



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')



if __name__ == "__main__":
    app.run(debug=True)
