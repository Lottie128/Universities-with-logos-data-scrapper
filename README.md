# Flask version of the University Scraper with logo and course scraping using BeautifulSoup and Tailwind UI


University Scraper - Flask App
==============================

This project is a simple Flask web application that allows users to either upload a CSV file or fetch university data from a GitHub-hosted JSON API.
It enriches this data by:
- Extracting the university logo via Clearbit's logo API.
- Attempting to scrape course offerings from topuniversities.com via Google Search.
- Outputting a WordPress-compatible CSV containing university name, country, website, logo filename, courses, and fees.

UI is built with TailwindCSS for a clean, modern frontend.

Features
--------
- Upload CSV file with `University`, `Country`, `Website` columns.
- OR use GitHub API with ~200 universities.
- Auto-fetch logos (Clearbit)
- Auto-scrape courses (Google + BeautifulSoup)
- Clean CSV output for WordPress import

Setup
-----
1. Install dependencies:
    ```bash
    pip install flask pandas requests beautifulsoup4
    ```
2. Run the app:
    ```bash
    python app.py
    ```
3. Open your browser:
    ```
    http://localhost:5000/
    ```
4. Choose to upload your CSV or use the GitHub dataset.
5. Download enriched CSV from `/download`

Folders
-------
- `uploads/` - stores uploaded CSVs
- `logos/` - stores downloaded logo images

Dependencies
------------
- Flask
- pandas
- requests
- BeautifulSoup4

Disclaimer
----------
- Course scraping is approximate (parsing Google's first result pointing to topuniversities.com).
- Logo URLs depend on domain presence and Clearbit availability.
- You may hit Google rate limits without proper headers or proxies.

License
-------
Free to use and modify.
"""
