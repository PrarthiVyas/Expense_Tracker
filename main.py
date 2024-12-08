from flask import Flask,request,render_template,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_user,logout_user,UserMixin,current_user,login_required
from forms import expenseForm

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
    print(current_user.id)

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
    #item = expenses.query.filter_by(id=id, user_id=current_user.id).first()
    
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
        return render_template('edit.html',form = form, ed = item)
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    logout_user()
    return render_template('login.html')
 
with app.app_context():
    db.create_all()
app.run(debug=True)

