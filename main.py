from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

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

    # Generate all possible combinations of the local part with dots
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

    # Limit the results
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

# Step 2: Automate account creation with each email
password = "Iloveindia123@"  # Hardcode your password here

for email in email_variations:
    # Set up Chrome options (optional: headless mode)
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment for no browser UI

    # Initialize a new WebDriver instance for each iteration
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        print(f"Attempting signup with {email}...")
        
        # Navigate to the Neo4j login/signup page
        driver.get("https://graphacademy.neo4j.com/login/?return=/")
        time.sleep(3)  # Wait for page load

        # Find and click the "Sign Up" link/button
        signup_link = driver.find_element(By.LINK_TEXT, "Sign up")
        signup_link.click()
        time.sleep(2)  # Wait for signup form to load

        # Fill out the email field and submit
        email_field = driver.find_element(By.ID, "email")
        email_submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        email_field.send_keys(email)
        email_submit_button.click()
        time.sleep(3)  # Wait for password field to appear

        # Fill out the password field and submit
        password_field = driver.find_element(By.ID, "password")
        password_submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        password_field.send_keys(password)
        password_submit_button.click()
        time.sleep(3)  # Wait for signup confirmation or redirect

        # Save the account details to accounts.txt in append mode
        with open("accounts.txt", "a") as account_file:
            account_file.write(f"Email: {email}, Password: {password}\n")
        print(f"Account created for {email} and saved to accounts.txt")

        # Navigate to the certifications page (optional)
        driver.get("https://graphacademy.neo4j.com/certifications")
        time.sleep(3)  # Wait for certifications page to load

    except Exception as e:
        print(f"An error occurred with {email}: {e}")

    finally:
        # Close the browser session after each iteration
        driver.quit()
        time.sleep(2)  # Small delay before starting the next session