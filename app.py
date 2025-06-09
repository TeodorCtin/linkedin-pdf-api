from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

app = Flask(__name__)

LINKEDIN_EMAIL = "duku.constantin@joben.eu"
LINKEDIN_PASSWORD = "LinkedIn2026@1234"

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "pdfs")
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def setup_driver(download_path):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    prefs = {
        "download.default_directory": download_path,
        "printing.print_preview_sticky_settings.appState": '{"recentDestinations":[{"id":"Save as PDF","origin":"local"}],"selectedDestinationId":"Save as PDF","version":2}',
        "savefile.default_directory": download_path
    }
    options.add_experimental_option('prefs', prefs)
    options.add_argument('--kiosk-printing')

    driver = webdriver.Chrome(options=options)
    return driver

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    data = request.json
    url = data.get('url')
    if not url or "linkedin.com/in" not in url:
        return jsonify({"error": "Invalid LinkedIn profile URL"}), 400

    driver = setup_driver(DOWNLOAD_FOLDER)

    try:
        driver.get("https://www.linkedin.com/login")
        time.sleep(2)

        driver.find_element(By.ID, "username").send_keys(LINKEDIN_EMAIL)
        driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        time.sleep(5)

        driver.get(url)
        time.sleep(5)

        profile_name = url.rstrip("/").split("/")[-1]
        filename = f"{profile_name}.pdf"
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)

        driver.execute_script('window.print();')

        time.sleep(5)

        if os.path.exists(file_path):
            return jsonify({"message": "PDF saved", "file": filename}), 200
        else:
            return jsonify({"error": "PDF not found after print"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
