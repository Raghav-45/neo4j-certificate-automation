from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

def generate_dot_trick_emails(email: str, limit: int = 10):
    """
    Generate a list of email variations using the Gmail dot trick.

    :param email: The base email address (e.g., example@gmail.com)
    :param limit: The maximum number of email variations to generate
    :return: A list of email variations
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
    unique_variations = list(dict.fromkeys(all_variations))  # Remove duplicates
    result_emails = [f"{variation}@{domain}" for variation in unique_variations[:limit]]
    
    return result_emails

# Step 1: Generate and save email variations
base_email = "adi4545aditya@gmail.com"  # Hardcode your base Gmail address here
email_variations = generate_dot_trick_emails(base_email, limit=10)

# Save emails to emails.txt
with open("emails.txt", "w") as email_file:
    for email in email_variations:
        email_file.write(f"{email}\n")
print(f"Generated {len(email_variations)} email variations and saved to emails.txt")

# Step 2 & 3: Check if accounts.txt exists and decide between login or signup
password = "Iloveindia123@"  # Hardcode your password here
accounts_file = "accounts.txt"

# Function to read accounts from accounts.txt
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

# Function to login with given credentials (two-step process)
def login(driver, email, password):
    print(f"Attempting login with {email}...")
    driver.get("https://graphacademy.neo4j.com/login/?return=/")
    time.sleep(3)  # Wait for page load

    # Step 1: Enter email and submit
    email_field = driver.find_element(By.ID, "username")
    email_submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    email_field.send_keys(email)
    email_submit_button.click()
    time.sleep(1)  # Wait for password field to appear

    # Step 2: Enter password and submit
    password_field = driver.find_element(By.ID, "password")
    password_submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    password_field.send_keys(password)
    password_submit_button.click()
    time.sleep(3)  # Wait for login to complete

    driver.get("https://graphacademy.neo4j.com/certifications/neo4j-certification/enrol/")
    time.sleep(30)  # Wait for certifications page
    print(f"Logged in with {email} and navigated to certifications page.")

# Check if accounts.txt exists and has data
existing_accounts = read_accounts(accounts_file)

if existing_accounts:
    # Step 3: Login with existing accounts
    for email, pwd in existing_accounts.items():
        chrome_options = Options()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        try:
            login(driver, email, pwd)
        except Exception as e:
            print(f"Login failed for {email}: {e}")
        finally:
            driver.quit()
            time.sleep(2)  # Delay before next login
else:
    # Step 2: Create new accounts if accounts.txt doesn’t exist or is empty
    for email in email_variations:
        chrome_options = Options()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            print(f"Attempting signup with {email}...")
            driver.get("https://graphacademy.neo4j.com/login/?return=/")
            time.sleep(3)  # Wait for page load

            signup_link = driver.find_element(By.LINK_TEXT, "Sign up")
            signup_link.click()
            time.sleep(2)  # Wait for signup form to load

            email_field = driver.find_element(By.ID, "email")
            email_submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            email_field.send_keys(email)
            email_submit_button.click()
            time.sleep(3)  # Wait for password field

            password_field = driver.find_element(By.ID, "password")
            password_submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            password_field.send_keys(password)
            password_submit_button.click()
            time.sleep(3)  # Wait for signup confirmation

            with open(accounts_file, "a") as account_file:
                account_file.write(f"Email: {email}, Password: {password}\n")
            print(f"Account created for {email} and saved to accounts.txt")

            driver.get("https://graphacademy.neo4j.com/certifications")
            time.sleep(3)  # Wait for certifications page

        except Exception as e:
            print(f"An error occurred with {email}: {e}")

        finally:
            driver.quit()
            time.sleep(2)  # Delay before next iteration