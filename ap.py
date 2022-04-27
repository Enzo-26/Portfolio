from flask import Flask, render_template, redirect, url_for, request, g

from flask_wtf import FlaskForm
from wtforms import DateTimeField, FloatField, TextAreaField
from wtforms.validators import DataRequired

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


#conn = db.connect("viewings.db")
#conn.execute("PRAGMA foreign_keys = 1")  

#cursor = conn.cursor()

#cursor.execute("SELECT * FROM movies")

#for row in cursor:
#    print(row)

class EntryForm(FlaskForm):
    order_size = FloatField("No. of tickets", validators=[DataRequired()])
    email = TextAreaField("Email")  # datanotrequired here but optional

@app.route("/detail", methods=["GET", "POST"])
def detail():
    v_id = request.args['v_id']
    db = get_db()
    details = db.execute('''
    select v.id, v.date_time as Time, m.Title, a.id as Auditorium, a.capacity as Capacity, m.description as Description, t.price as Price 
        from viewing v
    join movies m on v.movie_id = m.id 
    join auditorium a on v.audit_id = a.id 
    join tickets t on v.id = t.viewing_id
    where viewing_id = ?
    ''', v_id).fetchone()
    
    df = pd.read_sql_query('''
    select o.viewing_id, c.first_name, c.last_name, c.email, c.phone, o.tickets
from customers c
join orders o on c.email = o.email
    ''', db)
    
    df.loc['Total'] = df.sum(numeric_only=True, axis=1)
    df = df.iloc[:,1:]
    condition = "good"
    form = EntryForm()
    if form.validate_on_submit():
        emails = db.execute("select email from customers")
        if form.email.data in emails:
            
            cursor = db.cursor()
            cursor.execute("insert into orders values (?,?,?)", 
            [
                form.email.data,
                v_id,
                form.order_size.data
            ])
            cursor.close()
            return redirect('/')
            
        else:
            condition = "bad"


    return render_template('detail.html', details = details, df = df, form = form, condition = condition)

@app.route("/", methods=["GET", "POST"])
def homepage():
    db = get_db()
    db.row_factory=sqlite3.Row
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
    if request.form == "GET":
        v_id = request.form["v_id"]
        return redirect(url_for("detail", usr = v_id))   
        
    
    return render_template('homepage.html', viewings=viewings)
    



   # form = EntryForm()
#    if form.validate_on_submit():
 #       cursor = get_db().cursor()
  #      cursor.execute(
   #         "INSERT INTO orders([datetime], temperature, pressure, comment) VALUES (?, ?, ?, ?)",
    #        [
     #           form.order_size.data,
      #          form.email.data,
       #     ]
#        )
 #       cursor.close()
  #      return redirect('/')

    #return render_template('detail')



if __name__ == '__main__':
    app.run(debug=True)