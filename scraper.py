# ==========================
# IMPORT LIBRARIES
# ==========================

# ❌ Removed anvil imports (not needed in cloud)

import time                  # Used to add delays (important for Selenium stability)
import random                # Used to randomize delay (avoid bot detection)
import pandas as pd          # Used for storing and saving data to Excel
import os                    # Used for file handling (check if file exists)

# Selenium (browser automation)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Automatically installs correct ChromeDriver
from webdriver_manager.chrome import ChromeDriverManager


# ==========================
# MAIN SCRAPER FUNCTION
# ==========================
def run_bni_scraper(BASE_URL, OUTPUT_FILE):

    # ==========================
    # RESUME SYSTEM
    # ==========================

    try:
        existing_df = pd.read_excel(OUTPUT_FILE)
        collected_links = set(existing_df["Profile Link"].tolist())
        print(f"🔁 Resuming... {len(collected_links)} profiles already scraped")

    except:
        existing_df = pd.DataFrame()
        collected_links = set()

    data = []

    # ==========================
    # SETUP SELENIUM BROWSER
    # ==========================

    options = Options()

    # 🔥 IMPORTANT FOR CLOUD (HEADLESS MODE)
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    wait = WebDriverWait(driver, 15)


    # ==========================
    # LOAD MAIN PAGE
    # ==========================
    driver.get(BASE_URL)

    wait.until(EC.presence_of_element_located((By.XPATH, "//table")))


    # ==========================
    # GET ALL CHAPTER LINKS
    # ==========================
    elements = driver.find_elements(By.XPATH, "//a[contains(@href,'chapterdetail')]")

    chapter_links = []
    seen = set()

    for el in elements:
        link = el.get_attribute("href")
        if link and link not in seen:
            seen.add(link)
            chapter_links.append(link)

    print(f"📊 Total Chapters Found: {len(chapter_links)}")


    # ==========================
    # FUNCTION: EXTRACT CONTACT DETAILS
    # ==========================
    def scrape_member_details():

        phone, direct, chapter = "", "", ""

        try:
            more_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "moredots")))
            driver.execute_script("arguments[0].click();", more_btn)

            time.sleep(1)

            items = driver.find_elements(
                By.XPATH,
                "//div[contains(@class,'memberContactDetails')]//li"
            )

            for item in items:
                try:
                    label = item.find_element(By.TAG_NAME, "strong").text.strip().lower()
                    number = item.find_element(By.TAG_NAME, "a").text.strip()

                    if "phone" in label and not phone:
                        phone = number
                    elif ("direct" in label or "mobile" in label) and not direct:
                        direct = number

                except:
                    continue

            try:
                chapter = driver.find_element(
                    By.XPATH,
                    "//div[contains(@class,'memberContactDetails')]//p//a"
                ).text.strip()
            except:
                pass

        except:
            pass

        return phone, direct, chapter


    # ==========================
    # LOOP THROUGH CHAPTERS
    # ==========================
    for idx, chapter_url in enumerate(chapter_links):

        print(f"\n📘 Processing Chapter {idx+1}/{len(chapter_links)}")

        driver.get(chapter_url)
        time.sleep(random.uniform(2, 3))

        try:
            chapter_name = driver.find_element(By.TAG_NAME, "h1").text
        except:
            chapter_name = "Unknown"

        try:
            members_tab = wait.until(EC.element_to_be_clickable((By.ID, "members_tab")))
            driver.execute_script("arguments[0].click();", members_tab)

            wait.until(EC.presence_of_element_located((By.ID, "chapterListTable")))
            time.sleep(2)

        except:
            continue

        members = driver.find_elements(By.XPATH, "//table[@id='chapterListTable']//tbody/tr")

        print(f"👥 Members Found: {len(members)}")


        # ==========================
        # LOOP MEMBERS
        # ==========================
        for i in range(len(members)):

            try:
                members = driver.find_elements(By.XPATH, "//table[@id='chapterListTable']//tbody/tr")
                row = members[i]

                link_el = row.find_element(By.XPATH, "./td[1]/a")
                name = link_el.text
                profile_link = link_el.get_attribute("href")

                if profile_link in collected_links:
                    continue

                tds = row.find_elements(By.TAG_NAME, "td")

                company = tds[1].text if len(tds) > 1 else ""
                category = tds[2].text if len(tds) > 2 else ""

                driver.execute_script("window.open(arguments[0]);", profile_link)
                driver.switch_to.window(driver.window_handles[1])

                time.sleep(2)

                phone, direct, chapter_profile = scrape_member_details()

                if not chapter_profile:
                    chapter_profile = chapter_name

                try:
                    profession = driver.find_element(By.CSS_SELECTOR, "h6").text
                except:
                    profession = category

                try:
                    website = driver.find_element(
                        By.CSS_SELECTOR, ".textHolder a"
                    ).get_attribute("href")
                except:
                    website = ""

                row_data = {
                    "Name": name,
                    "Company": company,
                    "Profession": profession,
                    "Phone": phone,
                    "Direct": direct,
                    "Chapter": chapter_profile,
                    "Website": website,
                    "Profile Link": profile_link
                }

                data.append(row_data)

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except:
                continue


        # ==========================
        # SAVE AFTER EACH CHAPTER
        # ==========================
        if data:

            new_df = pd.DataFrame(data)

            if os.path.exists(OUTPUT_FILE):
                existing_df = pd.read_excel(OUTPUT_FILE)
                final_df = pd.concat([existing_df, new_df], ignore_index=True)
                final_df.drop_duplicates(subset=["Profile Link"], inplace=True)
            else:
                final_df = new_df

            final_df.to_excel(OUTPUT_FILE, index=False)

            collected_links.update(new_df["Profile Link"].tolist())
            data = []

            print(f"✅ Saved Chapter → {chapter_name}")


    # ==========================
    # FINISH
    # ==========================
    driver.quit()

    print("\n🎉 Scraping completed safely!")

    return OUTPUT_FILE