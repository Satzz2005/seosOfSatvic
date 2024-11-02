from flask import Flask, render_template, request
from seo3 import HybridSEOSystem  # Ensure this import is correct

app = Flask(__name__)
hybrid_seo = HybridSEOSystem()

@app.route('/', methods=['GET', 'POST'])
def home():
    results = []  # Initialize an empty list to hold search results
    if request.method == 'POST':
        keyword = request.form['keywords']  # Fetch the keywords from the form
        try:
            results = hybrid_seo.search_webpages(keyword)  # Call the search function
        except Exception as e:
            print(f"Error during search: {e}")  # Print the error to console for debugging
            results = []  # Optionally, you could set an error message in the results

    return render_template('index.html', results=results)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404  # Custom 404 page

if __name__ == '__main__':
    app.run(debug=True)
