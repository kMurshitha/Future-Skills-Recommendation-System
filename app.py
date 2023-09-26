from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app


# Load and preprocess your data and define your machine learning functions here
# ...

# Sample dataset (replace this with your actual dataset)
data = pd.read_csv(r'C:\Users\Mushfira\Desktop\newproj\skill - Sheet1 (9).csv')

# List of skills columns to consider for feature extraction
skills_columns = ['Basic skill 1', 'Basic skill 2',
                  'Basic skill 3', 'Basic skill 4']

# Convert all values in the skills columns to strings
for column in skills_columns:
    data[column] = data[column].astype(str)

# Combine the skills text from all columns into a single list
skills_text = data[skills_columns].apply(lambda x: ' '.join(x), axis=1)

# Initialize the TF-IDF vectorizer
tfidf_vectorizer = TfidfVectorizer()

# Fit and transform the skills text using TF-IDF
tfidf_matrix = tfidf_vectorizer.fit_transform(skills_text)

# Calculate pairwise cosine similarity
cosine_sim_matrix = cosine_similarity(tfidf_matrix)

# Convert the cosine similarity matrix to a DataFrame
cosine_sim_df = pd.DataFrame(
    cosine_sim_matrix, index=data.index, columns=data.index)

# Function to generate future skills and domains recommendations


def generate_recommendations(input_skills, num_recommendations=1):
    input_skills_text = ' '.join(input_skills)

    # Transform input skills using TF-IDF
    input_skills_tfidf = tfidf_vectorizer.transform([input_skills_text])

    # Calculate cosine similarities between input skills and all job roles
    cosine_similarities = cosine_similarity(
        input_skills_tfidf, tfidf_matrix).flatten()

    # Get indices of similar job roles
    similar_roles_indices = cosine_similarities.argsort(
    )[-num_recommendations-1:-1][::-1]

    # Create a dictionary to store recommendations by domain
    recommended_by_domain = {}

    for role_index in similar_roles_indices:
        role_name = data.loc[role_index, 'Domain']
        future_skills_str = data.loc[role_index, 'Future Skill']

        # Split the comma-separated string into a list of skills
        future_skills = [skill.strip()
                         for skill in future_skills_str.split(',')]

        # Check if the domain already exists in the dictionary
        if role_name in recommended_by_domain:
            recommended_by_domain[role_name]['Future Skills'].extend(
                future_skills)
        else:
            recommended_by_domain[role_name] = {
                'Domain': role_name, 'Future Skills': future_skills}

    return list(recommended_by_domain.values())


def generate_job_recommendations(input_skills):
    # Convert all input skills to lowercase to make the comparison case-insensitive
    input_skills = [skill.lower() for skill in input_skills]

    input_skills_text = ' '.join(input_skills)

    # Transform input skills using TF-IDF
    input_skills_tfidf = tfidf_vectorizer.transform([input_skills_text])

    # Calculate cosine similarities between input skills and all job roles
    cosine_similarities = cosine_similarity(
        input_skills_tfidf, tfidf_matrix).flatten()

    # Get indices of similar job roles
    similar_roles_indices = cosine_similarities.argsort()[::-1]

    # Create a set to store recommended domains
    recommended_domains = set()

    for role_index in similar_roles_indices:
        role_name = data.loc[role_index, 'Domain']
        role_skills = [data.loc[role_index, column].lower()
                       for column in skills_columns]

        # Check if all input skills are contained in the role skills (case-insensitive)
        if all(skill in role_skills for skill in input_skills):
            recommended_domains.add(role_name)

    return list(recommended_domains)


def generate_job_recommendations(input_skills):
    # Convert all input skills to lowercase to make the comparison case-insensitive
    input_skills = [skill.lower() for skill in input_skills]

    input_skills_text = ' '.join(input_skills)

    # Transform input skills using TF-IDF
    input_skills_tfidf = tfidf_vectorizer.transform([input_skills_text])

    # Calculate cosine similarities between input skills and all job roles
    cosine_similarities = cosine_similarity(
        input_skills_tfidf, tfidf_matrix).flatten()

    # Get indices of similar job roles
    similar_roles_indices = cosine_similarities.argsort()[::-1]

    # Create a set to store recommended domains
    recommended_domains = set()

    for role_index in similar_roles_indices:
        role_name = data.loc[role_index, 'Domain']
        role_skills = [data.loc[role_index, column].lower()
                       for column in skills_columns]

        # Check if all input skills are contained in the role skills (case-insensitive)
        if all(skill in role_skills for skill in input_skills):
            recommended_domains.add(role_name)

    return list(recommended_domains)
# Expose an API endpoint for recommendations


app.secret_key = "123"

con = sqlite3.connect("database.db")
con.execute("create table if not exists customer(pid integer primary key,name text,contact integer,mail text,password password)")
con.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(
            "select * from customer where name=? and password=?", (name, password))
        data = cur.fetchone()

        if data:
            session["name"] = data["name"]
            session["password"] = data["password"]
            return redirect("customer")
        else:
            flash("Username and Password Mismatch", "danger")
    return redirect(url_for("index"))


@app.route('/customer', methods=["GET", "POST"])
def customer():
    return render_template("customer.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form['name']
            contact = request.form['contact']
            mail = request.form['mail']
            password = request.form['password']
            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur.execute("insert into customer(name,contact,mail,password)values(?,?,?,?)",
                        (name, contact, mail, password,))
            con.commit()
            flash("Record Added  Successfully", "success")
        except:
            flash("Error in Insert Operation", "danger")
        finally:
            return redirect(url_for("index"))
            con.close()

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route('/skills')
def skills():
    return render_template('skills.html')


@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    print("Endpoint accessed")
    input_skills = request.json.get('skills', [])
    num_recommendations = request.json.get('num_recommendations', 1)

    recommendations = generate_recommendations(
        input_skills)
    print(recommendations)  # Print recommendations
    return jsonify(recommendations)


@app.route('/jobs')
def jobs():
    return render_template('jobs.html')


@app.route("/job_recommendations", methods=["GET", "POST"])
def job_recommendations():
    recommendations = []
    if request.method == "POST":
        input_skills = request.form["skills"].split(", ")
        print("Input Skills:", input_skills)  # Add this line for debugging
        recommendations = generate_job_recommendations(input_skills)
        # Add this line for debugging
        print("Recommendations:", recommendations)
    return render_template("jobs.html", recommendations=recommendations)


@app.route('/get_emerging_skills')
def get_emerging_skills():
    # Fetch and return the top 5 emerging skills from your data
    emerging_skills = ['Full Stack Development',
                       'UX/UI Design', 'Back-End Development', 'Cyber Security', 'Artificial Intelligence']
    return jsonify({'skills': emerging_skills})


@app.route('/get_emerging_jobs')
def get_emerging_jobs():
    # Fetch and return the top 5 emerging skills from your data
    emerging_jobs = ['Artificial intelligence',
                     'Computer security', 'Computing', 'Problem solving', 'Project management']
    return jsonify({'skills': emerging_jobs})


if __name__ == '__main__':
    app.run(debug=True)
