from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import time
import os
import random

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
    # Navigate to the certification test page
    driver.get("https://graphacademy.neo4j.com/certifications/neo4j-certification/enrol/")
    time.sleep(5)  # Wait for the page to load (adjust if needed)

    # Loop through 80 questions
    for question_num in range(1, 81):
        print(f"Answering question {question_num} for {email}...")
        try:
            # Check for radio buttons (multiple-choice)
            radio_options = driver.find_elements(By.XPATH, "//input[@name='answers' and @type='radio']")
            # Check for checkboxes (select all that apply)
            checkbox_options = driver.find_elements(By.XPATH, "//input[@name='answers' and @type='checkbox']")
            # Check for dropdown (select one from options)
            dropdown = driver.find_elements(By.XPATH, "//select[@name='answers']")
            # Check for text input (fill in the blank)
            text_input = driver.find_elements(By.XPATH, "//input[@name='answers']")  # Broader locator

            if radio_options:
                # Handle multiple-choice (select one)
                selected_option = random.choice(radio_options)
                selected_option.click()
                print(f"Selected radio option for question {question_num}")
            elif checkbox_options:
                # Handle select all that apply (select random subset)
                num_to_select = random.randint(1, len(checkbox_options))  # Select 1 to all options
                selected_options = random.sample(checkbox_options, num_to_select)
                for option in selected_options:
                    option.click()
                print(f"Selected {num_to_select} checkbox options for question {question_num}")
            elif dropdown:
                # Handle dropdown (select one option)
                select = Select(dropdown[0])  # Use Selenium's Select class
                options = [opt.get_attribute("value") for opt in select.options if opt.get_attribute("value")]  # Exclude empty option
                if options:
                    selected_value = random.choice(options)
                    select.select_by_value(selected_value)
                    print(f"Selected dropdown option '{selected_value}' for question {question_num}")
                else:
                    print(f"No valid dropdown options found for question {question_num}")
                    break
            elif text_input:
                text_field = text_input[0]
                answer = "p.name"  # Placeholder; adjust based on context if known
                text_field.clear()  # Clear any existing text
                text_field.send_keys(answer)
                print(f"Entered text '{answer}' for question {question_num}")
            else:
                print(f"No answer options found for question {question_num}.")
                break

            time.sleep(1)  # Delay to ensure the button enables

            # Find and click the "Submit Answer" button
            submit_button = driver.find_element(By.XPATH, "//button[contains(@class, 'btn--primary') and @type='submit']")
            if submit_button.is_enabled():
                submit_button.click()
                print(f"Submitted answer for question {question_num}")
            else:
                print(f"Submit button not enabled for question {question_num}")
                break
            time.sleep(2)  # Wait for the next question to load

        except Exception as e:
            print(f"Error on question {question_num} for {email}: {e}")
            break  # Exit loop if something goes wrong

    print(f"Completed certification test for {email}.")
    return True

# Check if accounts.txt exists and has data
existing_accounts = read_accounts(accounts_file)

if existing_accounts:
    # Step 3: Login with existing accounts and complete the test
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
    # Step 2: Create new accounts if accounts.txt doesn’t exist or is empty
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