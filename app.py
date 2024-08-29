from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objs as go
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load the data and model
data = pd.read_csv("static\\my\\Salary_Data.csv")
x = np.array(data['YearsExperience']).reshape(-1,1)
lr = LinearRegression()
lr.fit(x, np.array(data['Salary']))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    filtered_data = data.copy()
    if request.method == 'POST':
        if 'show_table' in request.form:
            show_table = True
        else:
            show_table = False

        filter_value = request.form.get('filter_value', 0, type=int)
        filtered_data = filtered_data.loc[filtered_data["YearsExperience"] >= filter_value]

        layout = go.Layout(
            xaxis=dict(range=[0, 16]),
            yaxis=dict(range=[0, 210000])
        )
        fig = go.Figure(data=go.Scatter(x=filtered_data["YearsExperience"], y=filtered_data["Salary"], mode='markers'), layout=layout)
        graph_html = fig.to_html(full_html=False)
        return render_template('home.html', show_table=show_table, data=filtered_data.to_html(classes='data', index=False), graph_html=graph_html)
    
    return render_template('home.html', show_table=False, data=None, graph_html=None)

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    predicted_salary = None
    if request.method == 'POST':
        years_experience = request.form.get('years_experience', type=float)
        if years_experience is not None:
            years_experience = np.array(years_experience).reshape(1, -1)
            predicted_salary = lr.predict(years_experience)[0]
            predicted_salary = round(predicted_salary)
    return render_template('prediction.html', predicted_salary=predicted_salary)

@app.route('/contribute', methods=['GET', 'POST'])
def contribute():
    if request.method == 'POST':
        experience = request.form.get('experience', type=float)
        salary = request.form.get('salary', type=float)
        if experience is not None and salary is not None:
            to_add = {"YearsExperience": [experience], "Salary": [salary]}
            to_add = pd.DataFrame(to_add)
            to_add.to_csv("static\\my\\Salary_Data.csv", mode='a', header=False, index=False)
            flash('Successfully submitted!', 'success')
            return redirect(url_for('contribute'))
    
    return render_template('contribute.html')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
