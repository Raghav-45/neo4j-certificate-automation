# First, install dependencies before any imports that require them
import os
import subprocess

def install_dependencies():
    """Install Chrome, ChromeDriver, and Python dependencies if not already installed."""
    # Check if Chrome is installed
    if not os.path.exists("/usr/bin/google-chrome"):
        print("Installing Google Chrome...")
        subprocess.run(["apt-get", "update"], check=True)
        subprocess.run(["apt-get", "install", "-y", "wget", "unzip", "libglib2.0-0", "libnss3", "libgconf-2-4", "libfontconfig1"], check=True)
        subprocess.run(["wget", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"], check=True)
        subprocess.run(["dpkg", "-i", "google-chrome-stable_current_amd64.deb"], check=False)
        subprocess.run(["apt-get", "-f", "install", "-y"], check=True)
        subprocess.run(["rm", "google-chrome-stable_current_amd64.deb"], check=True)
    
    # Get Chrome version
    chrome_version = subprocess.check_output(["google-chrome", "--version"]).decode().strip()
    print(f"Detected Chrome version: {chrome_version}")
    chrome_major_version = int(chrome_version.split()[2].split('.')[0])

    # Check if ChromeDriver is installed and compatible
    chromedriver_path = "/usr/local/bin/chromedriver"
    if os.path.exists(chromedriver_path):
        chromedriver_version = subprocess.check_output([chromedriver_path, "--version"]).decode().strip()
        chromedriver_major_version = int(chromedriver_version.split()[1].split('.')[0])
        if chromedriver_major_version == chrome_major_version:
            print(f"ChromeDriver {chromedriver_version} is compatible with Chrome {chrome_version}")
        else:
            print("ChromeDriver version mismatch, reinstalling...")
            os.remove(chromedriver_path)
    else:
        print("ChromeDriver not found, installing...")

    if not os.path.exists(chromedriver_path):
        chromedriver_url = f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_major_version}.0.6998.90/linux64/chromedriver-linux64.zip"
        subprocess.run(["wget", chromedriver_url], check=True)
        subprocess.run(["unzip", "chromedriver-linux64.zip", "-d", "/usr/local/bin/"], check=True)
        subprocess.run(["mv", "/usr/local/bin/chromedriver-linux64/chromedriver", chromedriver_path], check=True)
        subprocess.run(["rm", "-rf", "chromedriver-linux64", "chromedriver-linux64.zip"], check=True)
        print(f"Installed ChromeDriver for Chrome {chrome_major_version}")

    # Install Python dependencies
    print("Installing Python dependencies...")
    subprocess.run(["pip", "install", "selenium", "fuzzywuzzy", "python-Levenshtein"], check=True)

# Run installation before imports
install_dependencies()

# Now safe to import external packages
import time
import json
import random
import logging
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from fuzzywuzzy import fuzz, process

# Set up logging to a file
logging.basicConfig(filename='log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(message)s', filemode='a')

def generate_dot_trick_emails(email: str, limit: int = 50):
    """Generate a list of email variations using the Gmail dot trick."""
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

def read_accounts(file_path):
    """Read existing accounts from the CSV file."""
    accounts = {}
    if os.path.exists(file_path):
        with open(file_path, "r", newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                accounts[row['email']] = {'password': row['password'], 'test_score': row['test_score']}
    return accounts

def write_account(file_path, email, password, test_score="N/A"):
    """Write or update an account in the CSV file."""
    fieldnames = ['email', 'password', 'test_score']
    accounts = read_accounts(file_path)
    accounts[email] = {'password': password, 'test_score': test_score}
    
    with open(file_path, "w", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for email_key, data in accounts.items():
            writer.writerow({'email': email_key, 'password': data['password'], 'test_score': data['test_score']})

def login(driver, email, password):
    """Attempt login with provided credentials."""
    print(f"Attempting login with {email}...")
    logging.info(f"Attempting login with {email}")
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

def get_available_options(radio_options, checkbox_options, dropdown, text_input):
    """Retrieve the full text of available options for the question from <p> tags."""
    if radio_options:
        return [opt.find_element(By.XPATH, "./following-sibling::p").text.strip() for opt in radio_options]
    elif checkbox_options:
        return [opt.find_element(By.XPATH, "./following-sibling::p").text.strip() for opt in checkbox_options]
    elif dropdown:
        select = Select(dropdown[0])
        return [opt.text.strip() for opt in select.options if opt.get_attribute("value")]
    elif text_input:
        return ["text input"]  # Placeholder since text inputs don’t have predefined options
    return []

def select_random_answer(radio_options, checkbox_options, dropdown, text_input):
    """Select a random answer based on question type and return its value."""
    if radio_options:
        option = random.choice(radio_options)
        option.click()
        return option.get_attribute("value")
    elif checkbox_options:
        num_to_select = random.randint(1, len(checkbox_options))
        selected = random.sample(checkbox_options, num_to_select)
        for option in selected:
            option.click()
        return [opt.get_attribute("value") for opt in selected]
    elif dropdown:
        select = Select(dropdown[0])
        options = [opt for opt in select.options if opt.get_attribute("value")]
        if options:
            option = random.choice(options)
            select.select_by_value(option.get_attribute("value"))
            return option.get_attribute("value")
    elif text_input:
        text_field = text_input[0]
        text_field.clear()
        random_answer = "random_answer"  # Placeholder for text input
        text_field.send_keys(random_answer)
        return random_answer
    return None

def complete_certification_test(driver, email):
    """Complete the certification test and return the test status."""
    print(f"Starting certification test for {email}...")
    logging.info(f"Starting certification test for {email}")
    driver.get("https://graphacademy.neo4j.com/certifications/neo4j-certification/enrol/")
    time.sleep(5)

    for question_num in range(1, 81):
        print(f"Answering question {question_num} for {email}...")
        logging.info(f"Answering question {question_num} for {email}")
        try:
            question_elem = driver.find_element(By.XPATH, "//div[@id='content']/p")
            question_text = question_elem.text.strip()

            answer = ANSWERS.get(question_text, None)
            if not answer:
                best_match, score = process.extractOne(question_text, ANSWERS.keys(), scorer=fuzz.token_sort_ratio)
                if score >= 85:
                    answer = ANSWERS[best_match]
                    print(f"Fuzzy matched '{question_text}' to '{best_match}' (score: {score})")
                    logging.info(f"Fuzzy matched '{question_text}' to '{best_match}' (score: {score})")
                else:
                    print(f"No close match found for '{question_text}' (best score: {score}), using random answer...")
                    logging.info(f"No close match found for '{question_text}' (best score: {score}), using random answer")
                    radio_options = driver.find_elements(By.XPATH, "//input[@name='answers' and @type='radio']")
                    checkbox_options = driver.find_elements(By.XPATH, "//input[@name='answers' and @type='checkbox']")
                    dropdown = driver.find_elements(By.XPATH, "//select[@name='answers']")
                    text_input = driver.find_elements(By.XPATH, "//input[@name='answers']")
                    available_options = get_available_options(radio_options, checkbox_options, dropdown, text_input)
                    logging.info(f"Question not in answers.json: '{question_text}' - Available options: {available_options}")
                    select_random_answer(radio_options, checkbox_options, dropdown, text_input)
                    time.sleep(1)
                    submit_button = driver.find_element(By.XPATH, "//button[contains(@class, 'btn--primary') and @type='submit']")
                    if submit_button.is_enabled():
                        submit_button.click()
                        print(f"Submitted random answer for question {question_num}")
                        logging.info(f"Submitted random answer for question {question_num}")
                    else:
                        print(f"Submit button not enabled for question {question_num}")
                        logging.info(f"Submit button not enabled for question {question_num}")
                        break
                    time.sleep(1)
                    continue

            radio_options = driver.find_elements(By.XPATH, "//input[@name='answers' and @type='radio']")
            checkbox_options = driver.find_elements(By.XPATH, "//input[@name='answers' and @type='checkbox']")
            dropdown = driver.find_elements(By.XPATH, "//select[@name='answers']")
            text_input = driver.find_elements(By.XPATH, "//input[@name='answers']")

            if radio_options:
                if not isinstance(answer, str):
                    logging.info(f"Answer type mismatch for '{question_text}': Expected string, got {type(answer).__name__} - Using random answer")
                    random_answer = select_random_answer(radio_options, [], [], [])
                    print(f"Selected random radio option '{random_answer}' due to type mismatch")
                else:
                    option_found = False
                    for option in radio_options:
                        value = option.get_attribute("value")
                        if value == answer:
                            option.click()
                            print(f"Selected radio option '{value}'")
                            logging.info(f"Selected radio option '{value}'")
                            option_found = True
                            break
                    if not option_found:
                        available_options = get_available_options(radio_options, checkbox_options, dropdown, text_input)
                        logging.info(f"Answer '{answer}' not found in radio options for '{question_text}' - Available options: {available_options} - Using random answer")
                        random_answer = select_random_answer(radio_options, [], [], [])
                        print(f"Selected random radio option '{random_answer}' due to answer not found")
            elif checkbox_options:
                if not isinstance(answer, list):
                    logging.info(f"Answer type mismatch for '{question_text}': Expected list, got {type(answer).__name__} - Using random answer")
                    random_answer = select_random_answer([], checkbox_options, [], [])
                    print(f"Selected random checkbox options '{random_answer}' due to type mismatch")
                else:
                    for option in checkbox_options:
                        value = option.get_attribute("value")
                        if value in answer:
                            option.click()
                            print(f"Selected checkbox option '{value}'")
                            logging.info(f"Selected checkbox option '{value}'")
            elif dropdown:
                if not isinstance(answer, str):
                    logging.info(f"Answer type mismatch for '{question_text}': Expected string, got {type(answer).__name__} - Using random answer")
                    random_answer = select_random_answer([], [], dropdown, [])
                    print(f"Selected random dropdown option '{random_answer}' due to type mismatch")
                else:
                    try:
                        select = Select(dropdown[0])
                        select.select_by_value(answer)
                        print(f"Selected dropdown option '{answer}'")
                        logging.info(f"Selected dropdown option '{answer}'")
                    except Exception as e:
                        available_options = get_available_options(radio_options, checkbox_options, dropdown, text_input)
                        logging.info(f"Answer '{answer}' not found in dropdown for '{question_text}' - Available options: {available_options} - Using random answer")
                        random_answer = select_random_answer([], [], dropdown, [])
                        print(f"Selected random dropdown option '{random_answer}' due to answer not found: {e}")
            elif text_input:
                if not isinstance(answer, str):
                    logging.info(f"Answer type mismatch for '{question_text}': Expected string, got {type(answer).__name__} - Using random answer")
                    random_answer = select_random_answer([], [], [], text_input)
                    print(f"Entered random text '{random_answer}' due to type mismatch")
                else:
                    text_field = text_input[0]
                    text_field.clear()
                    text_field.send_keys(answer)
                    print(f"Entered text '{answer}'")
                    logging.info(f"Entered text '{answer}'")

            time.sleep(1)
            submit_button = driver.find_element(By.XPATH, "//button[contains(@class, 'btn--primary') and @type='submit']")
            if submit_button.is_enabled():
                submit_button.click()
                print(f"Submitted answer for question {question_num}")
                logging.info(f"Submitted answer for question {question_num}")
            else:
                print(f"Submit button not enabled for question {question_num}")
                logging.info(f"Submit button not enabled for question {question_num}")
                break
            time.sleep(1)

        except Exception as e:
            print(f"Error on question {question_num} for {email}: {e}")
            logging.error(f"Error on question {question_num} for {email}: {e}")
            break

    test_score = "Done"
    print(f"Completed certification test for {email}. Test status: {test_score}")
    logging.info(f"Completed certification test for {email}. Test status: {test_score}")
    return test_score

if __name__ == "__main__":
    # Check for answers.json
    if not os.path.exists("answers.json"):
        print("Please upload answers.json to Colab before running.")
        logging.error("answers.json not found. Please upload it.")
        from google.colab import files
        uploaded = files.upload()
        if "answers.json" not in uploaded:
            print("Error: answers.json not uploaded. Exiting.")
            logging.error("Error: answers.json not uploaded. Exiting.")
            exit(1)

    # Load answers from JSON file
    with open("answers.json", "r", encoding='utf-8') as f:
        ANSWERS = json.load(f)

    # Generate email variations
    base_email = "example@gmail.com"  # Replace with your Gmail address
    password = "Testpassword123@"  # Hardcode your password here
    email_variations = generate_dot_trick_emails(base_email, limit=25)
    print(f"Generated {len(email_variations)} email variations in memory")
    logging.info(f"Generated {len(email_variations)} email variations in memory")

    # Use CSV for accounts
    accounts_file = "accounts.csv"

    # Check accounts
    existing_accounts = read_accounts(accounts_file)
    emails_to_process = []

    for email in email_variations:
        if email in existing_accounts:
            if existing_accounts[email]['test_score'] == "Done":
                print(f"Test already completed for {email}, skipping...")
                logging.info(f"Test already completed for {email}, skipping")
            else:
                print(f"Test score is 'N/A' for {email}, adding to process list...")
                logging.info(f"Test score is 'N/A' for {email}, adding to process list")
                emails_to_process.append(email)
        else:
            print(f"Email {email} not in accounts, adding to process list...")
            logging.info(f"Email {email} not in accounts, adding to process list")
            emails_to_process.append(email)

    # Process emails
    if emails_to_process:
        for email in emails_to_process:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.binary_location = "/usr/bin/google-chrome"

            driver = None
            try:
                driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=chrome_options)
                print(f"Initialized headless Chrome for {email}")
                logging.info(f"Initialized headless Chrome for {email}")

                if email in existing_accounts:
                    test_score = login(driver, email, password)
                    write_account(accounts_file, email, password, test_score)
                    print(f"Updated {accounts_file} for {email}: Test Score: {test_score}")
                    logging.info(f"Updated {accounts_file} for {email}: Test Score: {test_score}")
                else:
                    print(f"Attempting signup with {email}...")
                    logging.info(f"Attempting signup with {email}")
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

                    print(f"Account created for {email}")
                    logging.info(f"Account created for {email}")
                    test_score = complete_certification_test(driver, email)
                    write_account(accounts_file, email, password, test_score)
                    print(f"Added to {accounts_file}: Email: {email}, Password: {password}, Test Score: {test_score}")
                    logging.info(f"Added to {accounts_file}: Email: {email}, Password: {password}, Test Score: {test_score}")

            except Exception as e:
                print(f"An error occurred with {email}: {e}")
                logging.error(f"An error occurred with {email}: {e}")

            finally:
                if driver is not None:
                    driver.quit()
                print(f"Closed headless Chrome for {email}")
                logging.info(f"Closed headless Chrome for {email}")
                time.sleep(2)

    else:
        print("No emails to process. All tests are either completed or not applicable.")
        logging.info("No emails to process. All tests are either completed or not applicable.")

    # Download results
    from google.colab import files
    files.download('accounts.csv')
    files.download('log.txt')