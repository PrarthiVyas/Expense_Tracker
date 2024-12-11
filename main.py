from flask import Flask,request,render_template,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_user,logout_user,UserMixin,current_user,login_required
from forms import expenseForm
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from datetime import date

import io
import re
matplotlib.use('Agg')  # Use a non-GUI backend (important for Flask)


import base64


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config["SECRET_KEY"] = "abc"
db=SQLAlchemy(app)
login_manager=LoginManager()
login_manager.login_view='login'
login_manager.init_app(app)

class user(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100),nullable=False)
    emailid=db.Column(db.String(100),nullable=False)
    password=db.Column(db.String(100),nullable=False)
    expenses = db.relationship('expenses', backref='user', lazy=True)

class expenses(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    expense=db.Column(db.String(100),nullable=False)
    amount=db.Column(db.Float,nullable=False)
    date=db.Column(db.Date,nullable=False)
    description=db.Column(db.String(500),nullable=False)
    category=db.Column(db.String(100),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        emailid=request.form.get('emailid')
        new_user=user(username=username,emailid=emailid,password=password)
        db.session.add(new_user)
        db.session.commit()  
        abc = user.query.all()
        for i in abc:
            print(i.username)
        return render_template('login.html') 
    return render_template('index.html')
    
@app.route('/',methods=['POST','GET'])
def login():
    if request.method=='POST':
        user_name=request.form.get('name')
        password=request.form.get('password')
        abc=user.query.filter_by(emailid=user_name).first()
        if abc and abc.password==password:
            login_user(abc)
            return redirect(url_for('add'))
        else:
            flash('Invalid Username/Password!','p_error')
            return redirect(url_for('login'))
    return render_template('login.html')

@login_manager.user_loader
def loader_user(user_id):
    return user.query.get(user_id)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/add',methods=['GET','POST'])
@login_required
def add():
    form=expenseForm()
    abc = expenses.query.filter_by(user_id=current_user.id)
    total_sum = sum(a.amount for a in abc)

    if request.method=='POST':
        ex= form.expense.data
        d = form.date.data
        c = form.category.data
        desc = form.description.data  
        a=form.amount.data
        new_expense=expenses(expense=ex,date=d,category=c,description=desc,amount=a,user_id=current_user.id)  
        db.session.add(new_expense)
        db.session.commit()
        flash("Added Successfully !!",'success')
        return redirect(url_for('add',total = total_sum))
    return render_template('add.html',form=form,data=abc, total = total_sum)

@app.route('/delete/<int:id>')
def delete(id):
    item=expenses.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash("Deleted Successfully !!",'success')
    return redirect(url_for('add'))

@app.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    form = expenseForm()
    item = expenses.query.get(id)
    
    if request.method == 'POST':
        item.expense = form.expense.data
        item.date = form.date.data
        item.category = form.category.data
        item.description = form.description.data  
        item.amount =form.amount.data
        db.session.commit()
        flash("Updated Successfully !!",'success')
        return redirect(url_for('add'))
    
    if request.method == 'GET':  # For GET request, populate the form
        form.expense.data = item.expense
        form.amount.data = item.amount
        form.description.data = item.description
        form.category.data = item.category
        form.date.data = item.date

        return render_template('edit.html',form = form)
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    logout_user()
    return render_template('login.html')


@app.route("/chart")
@login_required
def chart():
    abc=expenses.query.filter_by(user_id=current_user.id).all()
    unique_categor=[]
    unique_categor_count=[]
    items=[]
    print(abc)

    #Category wise pie chart for expense 
    for item in abc:
        if item.category not in unique_categor and item.expense!="Income":
            unique_categor.append(item.category)
            unique_categor_count.append(unique_categor.count(item.category))
        elif item.category in unique_categor and item.expense!="Income":
            unique_categor_count[unique_categor.index(item.category)]+=1

    
    unique_categor_num=np.array(unique_categor)
    unique_categor_count_num=np.array(unique_categor_count)
    print(unique_categor_count_num,unique_categor_num)
    chart1=create_pie_chart(unique_categor_count_num, unique_categor_num, title="Expense Category Count")




    #chart2
    months=[]
    expense_per_month=[]


    for item in abc:
        my_date = item.date
        month = my_date.month


        if month not in months and item.expense!="Income":
            months.append(month)
            expense_per_month.append(item.amount)
        elif month in months and item.expense != "Income":
            expense_per_month[months.index(month)]=expense_per_month[months.index(month)]+item.amount
        else:
            continue
    
    months_num=np.array(months)
    print(months_num)
    expense_per_month_num=np.array(expense_per_month)
    print(expense_per_month_num)
    chart2=create_bar_chart(expense_per_month_num,months_num,title="Expense per month")

    charts = [chart1,chart2]


    return render_template("chart.html", chart=charts)

def create_pie_chart(values, labels, title="Pie Chart"):
    """Creates a pie chart and returns it as a Base64 image."""
    plt.figure(figsize=(6, 6))  # Set figure size
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(title)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()  # Free memory
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return plot_data

def create_bar_chart(values, labels, title="Bar Chart"):
    """Creates a bar chart and returns it as a Base64 image."""
    plt.figure(figsize=(8, 6))  # Set figure size
    plt.bar(labels, values, color='skyblue')
    plt.title(title)
    plt.xlabel("Category")
    plt.ylabel("Amount")

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()  # Free memory
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return plot_data


 
with app.app_context():
    db.create_all()
app.run(debug=True)

