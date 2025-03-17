from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import time
import os
import json
from fuzzywuzzy import fuzz, process

def generate_dot_trick_emails(email: str, limit: int = 10):
    """
    Generate a list of email variations using the Gmail dot trick.
    """
    if "@" not in email:
        raise ValueError("Invalid email address")

    local, domain = email.split("@")
    if domain != "gmail.com":
        raise ValueError("This trick only works with Gmail addresses")

    def insert_dots(s):
        result = []
        n = len(s)
        for i in range(1, 1 << (n - 1)):
            parts = []
            for j in range(n):
                parts.append(s[j])
                if i & (1 << j):
                    parts.append(".")
            result.append("".join(parts))
        return result

    all_variations = [local] + insert_dots(local)
    unique_variations = list(dict.fromkeys(all_variations))
    result_emails = [f"{variation}@{domain}" for variation in unique_variations[:limit]]
    
    return result_emails

# Load answers from JSON file
with open("answers.json", "r") as f:
    ANSWERS = json.load(f)

# Step 1: Generate and save email variations
base_email = "adi4545aditya@gmail.com"  # Hardcode your base Gmail address here
email_variations = generate_dot_trick_emails(base_email, limit=10)

with open("emails.txt", "w") as email_file:
    for email in email_variations:
        email_file.write(f"{email}\n")
print(f"Generated {len(email_variations)} email variations and saved to emails.txt")

# Step 2 & 3: Check if accounts.txt exists and decide between login or signup
password = "Iloveindia123@"  # Hardcode your password here
accounts_file = "accounts.txt"

def read_accounts(file_path):
    accounts = {}
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            for line in file:
                if "Email:" in line and "Password:" in line:
                    email = line.split("Email: ")[1].split(",")[0].strip()
                    pwd = line.split("Password: ")[1].strip()
                    accounts[email] = pwd
    return accounts

def login(driver, email, password):
    print(f"Attempting login with {email}...")
    driver.get("https://graphacademy.neo4j.com/login/?return=/")
    time.sleep(3)

    email_field = driver.find_element(By.ID, "username")
    email_submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    email_field.send_keys(email)
    email_submit_button.click()
    time.sleep(1)

    password_field = driver.find_element(By.ID, "password")
    password_submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    password_field.send_keys(password)
    password_submit_button.click()
    time.sleep(3)

    return complete_certification_test(driver, email)

def complete_certification_test(driver, email):
    driver.get("https://graphacademy.neo4j.com/certifications/neo4j-certification/enrol/")
    time.sleep(5)

    for question_num in range(1, 81):
        print(f"Answering question {question_num} for {email}...")
        try:
            # Get question text
            question_elem = driver.find_element(By.XPATH, "//div[@id='content']/p")
            question_text = question_elem.text.strip()

            # Look up answer with fuzzy matching
            answer = ANSWERS.get(question_text, None)
            if not answer:
                # Fuzzy match if exact match fails
                best_match, score = process.extractOne(question_text, ANSWERS.keys(), scorer=fuzz.token_sort_ratio)
                if score >= 85:  # Threshold for similarity
                    answer = ANSWERS[best_match]
                    print(f"Fuzzy matched '{question_text}' to '{best_match}' (score: {score})")
                else:
                    print(f"No close match found for '{question_text}' (best score: {score}), skipping...")
                    continue  # Skip if no good match

            # Check question type
            radio_options = driver.find_elements(By.XPATH, "//input[@name='answers' and @type='radio']")
            checkbox_options = driver.find_elements(By.XPATH, "//input[@name='answers' and @type='checkbox']")
            dropdown = driver.find_elements(By.XPATH, "//select[@name='answers']")
            text_input = driver.find_elements(By.XPATH, "//input[@name='answers']")

            if radio_options:
                for option in radio_options:
                    value = option.get_attribute("value")
                    if value == answer:
                        option.click()
                        print(f"Selected radio option '{value}'")
                        break
            elif checkbox_options:
                if isinstance(answer, list):
                    for option in checkbox_options:
                        value = option.get_attribute("value")
                        if value in answer:
                            option.click()
                            print(f"Selected checkbox option '{value}'")
            elif dropdown:
                select = Select(dropdown[0])
                select.select_by_value(answer)
                print(f"Selected dropdown option '{answer}'")
            elif text_input:
                text_field = text_input[0]
                text_field.clear()
                text_field.send_keys(answer)
                print(f"Entered text '{answer}'")

            time.sleep(3)
            submit_button = driver.find_element(By.XPATH, "//button[contains(@class, 'btn--primary') and @type='submit']")
            if submit_button.is_enabled():
                submit_button.click()
                print(f"Submitted answer for question {question_num}")
            else:
                print(f"Submit button not enabled for question {question_num}")
                break
            time.sleep(2)

        except Exception as e:
            print(f"Error on question {question_num} for {email}: {e}")
            break

    print(f"Completed certification test for {email}.")
    return True

# Check if accounts.txt exists and has data
existing_accounts = read_accounts(accounts_file)

if existing_accounts:
    for email, pwd in existing_accounts.items():
        chrome_options = Options()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        try:
            login(driver, email, pwd)
        except Exception as e:
            print(f"Login failed for {email}: {e}")
        finally:
            driver.quit()
            time.sleep(2)
else:
    for email in email_variations:
        chrome_options = Options()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            print(f"Attempting signup with {email}...")
            driver.get("https://graphacademy.neo4j.com/login/?return=/")
            time.sleep(3)

            signup_link = driver.find_element(By.LINK_TEXT, "Sign up")
            signup_link.click()
            time.sleep(2)

            email_field = driver.find_element(By.ID, "email")
            email_submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            email_field.send_keys(email)
            email_submit_button.click()
            time.sleep(3)

            password_field = driver.find_element(By.ID, "password")
            password_submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            password_field.send_keys(password)
            password_submit_button.click()
            time.sleep(3)

            with open(accounts_file, "a") as account_file:
                account_file.write(f"Email: {email}, Password: {password}\n")
            print(f"Account created for {email} and saved to accounts.txt")

            complete_certification_test(driver, email)

        except Exception as e:
            print(f"An error occurred with {email}: {e}")

        finally:
            driver.quit()
            time.sleep(2)