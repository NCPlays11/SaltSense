from flask import Flask, render_template, jsonify, redirect, flash, request, url_for
import pandas as pd
import os
import csv
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
app.config["SECRET_KEY"] = os.getenv("FLASK_KEY")

file_path = os.path.join(app.root_path, "static", "desalination_data.csv")
df = pd.read_csv(file_path)

def server_only(f):
    def wrapper(*args, **kwargs):
        flash("This page is restricted...", "danger")
        return redirect(url_for('home'))
    wrapper.__name__ = f.__name__
    return wrapper

def value_in_csv(file_path, value, column_name):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row[column_name] == value:
                return True
    return False

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("About.html")

@app.route("/faq")
def faq():
    return render_template("FAQ.html", name="FAQ", title="FAQ")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

@app.route("/learn")
def learn():
    return render_template("learn.html", regions=["Middle East", "North America", "Asia Pacific", "Europe", "Africa"])

@app.route("/join")
def join():
    return render_template("join.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        CSV_FILE = os.path.join(app.root_path, "static", "contact.csv")
        # Form data
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        
        if name and email and message:
            if not os.path.exists(CSV_FILE):
                with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Full Name", "Email Address", "Message"])

            # Save data to CSV
            with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([name, email, message])

            # Flash a success message
            flash("Your message has been sent successfully!", "success")
        else:
            # Flash an error message if any field is missing
            flash("Please fill out all the fields.", "danger")
        
        # Redirect
        return redirect(url_for("contact"))
    
    # Render contact page
    return render_template("contact.html")

@app.route("/data")
@server_only
def get_data():
    data = df.to_dict(orient="records")
    return jsonify(data)

@app.route('/region/<region_name>')
def region_charts(region_name):
    if region_name not in df['Region'].unique().tolist():
        flash("This is not a valid region", "danger")
        return redirect(url_for("learn"))
    region_data = df[df['Region'] == region_name].to_dict(orient='records')
    return render_template('region_charts.html', region=region_name, data=region_data)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if email:
        # Define the file path within the 'static' directory
        file_path = os.path.join(app.root_path, "static", "subscribers.csv")
        # Check if email already exists
        if value_in_csv(file_path, email, "Email"):
            flash("You are already subscribed!", "danger")
        else:
            # Save the email to the CSV file
            with open(file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([email])
            
            # Flash a success message
            flash('You have successfully subscribed!', 'success')
    else:
        flash('Please provide a valid email address.', 'danger')
    
    return redirect(url_for('home'))

@app.errorhandler(405)
def method_not_allowed(error):
    flash("You cannot subscribe that way.", "danger")
    return redirect(url_for("home"))

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)