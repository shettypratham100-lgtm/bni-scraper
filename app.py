from flask import Flask, request, send_file
from scraper import run_bni_scraper
import os
app = Flask(__name__)

@app.route("/scrape")
def scrape():
    link = request.args.get("link")
    filename = request.args.get("filename")

    # ✅ Validate inputs
    if not link or not filename:
        return "Error: Missing link or filename", 400

    try:
        file_path = run_bni_scraper(link, filename + ".xlsx")

        # ✅ Check if file exists
        if not os.path.exists(file_path):
            return "Error: File not generated", 500

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Error: {str(e)}", 500

# Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
