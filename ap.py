from flask import Flask, render_template, redirect, url_for, request, g

from flask_wtf import FlaskForm
from matplotlib.style import available
from wtforms import DateTimeField, FloatField, TextAreaField
from wtforms.validators import DataRequired, NumberRange

import sqlite3 
import secrets
import datetime
from io import StringIO

import pandas as pd
import matplotlib as mpl
mpl.use('Agg')  # This is needed to be able to use Matplotlib in a sever application
import matplotlib.pyplot as plt
import seaborn as sns


app = Flask(__name__)

# print(secrets.token_hex())
app.secret_key = 'dcccc03f2b87d60942849204d6628141ec6da9d83c63115abeb1fafd14460636'

DATABASE = 'viewings.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, isolation_level=None)
    return db

# this function is to close the database
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

class EntryForm(FlaskForm):
    order_size = FloatField("No. of tickets", validators=[DataRequired(), NumberRange(min = 1)], default = 1)
    email = TextAreaField("Email")  # datanotrequired here but optional

@app.route("/detail", methods=["GET", "POST"])
def detail():
    # get viewing id 
    v_id = request.args['v_id']
    db = get_db()

    # get display results, fethcone() since we only need one viewing
    details = db.execute('''
    select v.id, v.date_time as Time, m.Title, a.id as Auditorium, a.capacity as Capacity, m.description as Description, t.price as Price 
        from viewing v
    join movies m on v.movie_id = m.id 
    join auditorium a on v.audit_id = a.id 
    join tickets t on v.id = t.viewing_id
    where viewing_id = ?
    ''', v_id).fetchone()
    
    # display info of users who ordered tickets
    df = pd.read_sql_query('''
    select o.viewing_id, c.first_name as 'First Name', c.last_name as 'Last Name', c.email as Email, c.phone as Phone, o.tickets as Tickets
    from customers c
    join orders o on c.email = o.email
    where o.viewing_id = ?
    ''', db, index_col = 'Last Name', params = (v_id))

    # add total row showing the total tickets purchased 
    df.loc['Total'] = df.sum(numeric_only=True)
    df = df.iloc[:,1:]
    # remove NaN values displayed from dataframe 
    df = df.fillna("")

    # set condition to good and then later to bad to help html if statement know when user email is not registered
    condition = "good"
    form = EntryForm()

    # start process to check if order size is larger than capacity
    audit = str(details[3])
    capacity = db.execute("select capacity from auditorium where id = ?", audit).fetchone()
    # get value
    capacity=capacity[0]
    sold = db.execute("select sum(tickets) from orders where viewing_id = ?", v_id).fetchone()
    # get value
    sold = sold[0]
    if sold == None:
        sold = 0
    # get available seats
    available = capacity - sold
    # condition to help with html if statement of whether order exceeds maximum available capacity 
    condition_2 = "good"
    if form.validate_on_submit():
        # checking if email is registered in the database
        emails = db.execute("select email from customers where email= ?",
        [form.email.data])
        res = emails.fetchone()
        if res == None:
            # when condition = "bad" html will display warning message
            condition = "bad"
        else:
            cursor = db.cursor()
            if form.order_size.data > available:
                condition_2 = "bad"
            else:

                cursor.execute(''' insert into orders values (?,?,?) on conflict(email, viewing_id) do update set tickets = tickets + ? ''', 
                    [
                    form.email.data,
                    v_id,
                    form.order_size.data,
                    str(form.order_size.data)
                    ])
                cursor.close()
                

    return render_template('detail.html', details = details, df = df, form = form, condition = condition, available = available, condition_2 = condition_2)

@app.route("/", methods=["GET", "POST"])
def homepage():
    db = get_db()
    # get table for the viewings
    viewings = db.execute(
        '''
        select v.id, v.date_time as Time, m.Title, a.id as Auditorium, t.price as Price 
        from viewing v
        join movies m on v.movie_id = m.id 
        join auditorium a on v.audit_id = a.id 
        join tickets t on v.id = t.viewing_id
        order by Time asc 
    
        ''', 
    ).fetchall()    
    # 
    if request.form == "GET":
        # we have get request at the button more info, which should redirect to details page for specified viewing
        # each row has a viewing id which we have assgined to the button in html code for homepage.html
        return redirect(url_for("detail"))   
        
    
    return render_template('homepage.html', viewings = viewings)
    

if __name__ == '__main__':
    app.run(debug=True)