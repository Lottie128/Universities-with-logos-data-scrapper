# Flask version of the University Scraper with logo and course scraping using BeautifulSoup and Tailwind UI

import os
import time
import pandas as pd
import requests
from urllib.parse import urlparse
from flask import Flask, request, redirect, send_file, Response
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
LOGO_DIR = 'logos'
OUTPUT_FILE = 'top_universities_enriched.csv'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOGO_DIR, exist_ok=True)

CSV_FALLBACK_URL = "https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json"
LIMIT = 200

def get_domain(url):
    try:
        return urlparse(url).netloc
    except:
        return ""

def get_logo(domain, filename):
    if not domain:
        return ""
    logo_url = f"https://logo.clearbit.com/{domain}"
    path = os.path.join(LOGO_DIR, filename)
    try:
        response = requests.get(logo_url, timeout=5)
        if response.status_code == 200 and "image" in response.headers.get("Content-Type", ""):
            with open(path, "wb") as f:
                f.write(response.content)
            return path
    except:
        pass
    return ""

def get_courses(university_name):
    try:
        query = university_name.replace(" ", "+") + "+site:topuniversities.com"
        search_url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        search_response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(search_response.text, "html.parser")
        link = soup.find("a", href=True)
        if not link:
            return ""

        topuni_url = link['href']
        topuni_response = requests.get(topuni_url, headers=headers)
        course_soup = BeautifulSoup(topuni_response.content, "html.parser")

        course_list = course_soup.select(".field--name-field-subjects a, .course-category-title")
        return "; ".join([tag.get_text(strip=True) for tag in course_list])
    except Exception:
        return ""

def fetch_from_github():
    response = requests.get(CSV_FALLBACK_URL)
    data = response.json()[:LIMIT]
    records = [{
        "University": uni.get("name", "").strip(),
        "Country": uni.get("country", "").strip(),
        "Website": uni.get("web_pages", [""])[0]
    } for uni in data]
    return pd.DataFrame(records)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        use_github = request.form.get("use_github") == "true"
        if not use_github and 'file' not in request.files:
            return "No file uploaded.", 400

        if use_github:
            df = fetch_from_github()
        else:
            file = request.files['file']
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            df = pd.read_csv(file_path)

        df["University"] = df["University"].astype(str)
        df["Country"] = df["Country"].astype(str)
        df["Website"] = df["Website"].astype(str)
        df["Domain"] = df["Website"].apply(get_domain)

        results = []
        for idx, row in df.iterrows():
            uni = row["University"]
            domain = row["Domain"]
            logo_file = get_logo(domain, uni.replace(" ", "_").replace("/", "_") + ".png")
            courses = get_courses(uni)
            results.append({
                "Post Type": "university",
                "University": uni,
                "Country": row["Country"],
                "Website": row["Website"],
                "Logo Filename": os.path.basename(logo_file) if logo_file else "",
                "Courses": courses,
                "Fees": ""
            })

        final_df = pd.DataFrame(results)
        final_df.to_csv(OUTPUT_FILE, index=False)
        return redirect("/download")

    return Response('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>University Scraper</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100 flex items-center justify-center min-h-screen">
            <div class="bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
                <h2 class="text-2xl font-bold text-center mb-6">🎓 University Import Tool</h2>
                <form method="post" enctype="multipart/form-data" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Upload CSV File</label>
                        <p class="text-xs text-gray-500">This will just download around 200 university names and their logos link mostly for wordpress developers making a study aboard platform to easily populate their database.</p>
                        <input type="file" name="file" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3" />
                    </div>
                    <div class="flex justify-between">
                        <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md">Import CSV</button>
                        <button type="submit" name="use_github" value="true" class="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-md">Use GitHub List</button>
                    </div>
                </form>
            </div>
        </body>
        </html>
    ''', mimetype='text/html')

@app.route("/download")
def download():
    return send_file(OUTPUT_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
