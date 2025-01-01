from flask_wtf import FlaskForm
from wtforms import SubmitField,DateField,FloatField,StringField,SelectField
from wtforms.validators import DataRequired


choiceType=['Expens','Income']
class expenseForm(FlaskForm):
    expense=SelectField("Expense/Income",choices=choiceType)
    amount=FloatField("Amount",validators=[DataRequired()])
    date=DateField("Date",validators=[DataRequired()])
    description=StringField("Description",validators=[DataRequired()])
    category=SelectField(label='State', choices=['Bills', 'Food', 'Shopping','Transport','Medical','Rent','Money Transfer'])
    submit = SubmitField("Save")


