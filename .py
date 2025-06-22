from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import time
import os

def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # Uncomment for headless run
    return webdriver.Chrome(options=options)

def load_old_prices():
    if os.path.exists("prices.json"):
        with open("prices.json", "r") as f:
            return json.load(f)
    return {}

def save_new_prices(data):
    with open("prices.json", "w") as f:
        json.dump(data, f, indent=2)

def scrape_zepto_products():
    driver = setup_driver()
    driver.get("https://www.zepto.in/")

    print("Waiting for page to load...")
    time.sleep(8)  # Allow time for page load and product rendering

    # Optional: Scroll to load more products
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    product_cards = driver.find_elements(By.CLASS_NAME, "ProductCard__container")
    products = []

    for card in product_cards:
        try:
            name = card.find_element(By.CLASS_NAME, "ProductCard__name").text
            price = card.find_element(By.CLASS_NAME, "ProductPrice__container").text
            products.append({"name": name, "price": price})
        except:
            continue

    driver.quit()
    return products

def compare_prices(old_data, new_data):
    changes = []
    old_prices = {item["name"]: item["price"] for item in old_data}

    for product in new_data:
        name = product["name"]
        new_price = product["price"]
        old_price = old_prices.get(name)

        if old_price and old_price != new_price:
            changes.append({
                "name": name,
                "old": old_price,
                "new": new_price
            })
    return changes

def main():
    print("Scraping Zepto products...")
    new_data = scrape_zepto_products()
    old_data = load_old_prices()

    if old_data:
        changes = compare_prices(old_data, new_data)
        if changes:
            print("📢 Price changes detected:")
            for c in changes:
                print(f"{c['name']}: {c['old']} → {c['new']}")
        else:
            print("✅ No price changes.")
    else:
        print("🆕 First run: saving initial prices.")

    save_new_prices(new_data)

if __name__ == "__main__":
    main()
