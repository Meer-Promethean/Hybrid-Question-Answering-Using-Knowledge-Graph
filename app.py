from flask import Flask, render_template, request

from bert import *
from Knowledge_graph import *
import pandas as pd, numpy as np

#Init app
app = Flask(__name__)

@app.route("/")
def index():
	return render_template("home.html") 

@app.route('/', methods=['POST'])
def my_form_post():
    query = request.form['query']
    if query != "":
        context = ""
		# Open a file with access mode 'a'
        file_object = open('dataset.txt', 'a')
        file_object.write(query+" \n")
		#we pass this query to get_context() function and it return the context of question if exist
        context = get_context(query)
        print(len(context))
        # context = "When does academic year starts in FAST NUCES? Academic Year of the university starts in August/September. Academic Year of the university ends in May/June. What is number of semesters in academic year? There are two regular semesters, namely, Fall and Spring, in an academic year."
        try:
            prediction = predict(context[:1000],query)
        except:
            prediction = "Please contact academic office for this query."
        if  len(context) <= 5 or prediction == "[SEP]" or prediction == "[CLS]" or prediction == "" :
            prediction = "Please contact academic office for this query."
        prediction = "Answer: "+ prediction+"\n"
        file_object.write(prediction)
        file_object.close()
    else:
        prediction = "Question is not valid"
    return render_template("home.html", answer=prediction) 

@app.route('/about')
def about():
	return render_template('about.html')


#Run Server
if __name__ == "__main__":
	app.run(debug=True)
