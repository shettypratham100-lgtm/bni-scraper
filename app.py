from flask import Flask, request, send_file
from scraper import run_bni_scraper

app = Flask(__name__)

@app.route("/scrape")
def scrape():
    # Get values from frontend
    link = request.args.get("link")
    filename = request.args.get("filename")

    # Run scraper
    file_path = run_bni_scraper(link, filename + ".xlsx")

    # Send file to user
    return send_file(file_path, as_attachment=True)

# Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)