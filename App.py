from flask import Flask, render_template, request

app = Flask(__name__)

# Import your Python program
import pandas as pd
import re
import numpy as np
from sklearn.feature_extraction import text
from sklearn.metrics.pairwise import cosine_similarity

# Load and preprocess the data
data = pd.read_csv("Instagram data.csv")
data = data[["Caption", "Hashtags"]]

def clean_text(text):
    return re.sub(r'[\ufffd]', '', text)

data["Caption"] = data["Caption"].apply(clean_text)
data["Hashtags"] = data["Hashtags"].apply(clean_text)

captions = data["Caption"].tolist()

# Vectorize and calculate similarities
uni_tfidf = text.TfidfVectorizer(stop_words="english")
uni_matrix = uni_tfidf.fit_transform(captions)
uni_sim = cosine_similarity(uni_matrix)

def recommend_post(new_caption, data, uni_tfidf, uni_sim):
    # Vectorize the new caption
    new_vec = uni_tfidf.transform([new_caption])

    # Calculate similarity between the new caption and existing captions
    new_sim = cosine_similarity(new_vec, uni_matrix)

    # Get the indices of the top 5 most similar captions
    top_indices = new_sim.argsort()[0][-5:-1]

    # Filter out empty strings from top_indices
    top_indices = [i for i in top_indices if i != '']

    # If there are fewer than 4 recommendations, return an empty string
    if len(top_indices) < 4:
        return ''

    recommended = ", ".join(data["Caption"].iloc[top_indices])
    return recommended

# Define a route for the homepage
@app.route('/')
def home():
    return render_template('index.html')

# Define a route for running your Python program
@app.route('/run', methods=['POST'])
def run_program():
    # Get the input data from the form
    new_caption = request.form.get('new_caption')

    # Run your Python program with the input data
    recommended_posts = recommend_post(new_caption, data, uni_tfidf, uni_sim)

    # Render the result on the result.html template
    return render_template('result.html', recommended_posts=recommended_posts)

if __name__ == '__main__':
    app.run(debug=True)