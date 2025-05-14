import time
import random
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Setup the Selenium WebDriver with anti-detection features
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Remove the navigator.webdriver property to avoid detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

# Scroll down to load more products
def scroll_down(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(2, 4))

# Extract product data from the page
def extract_product_data(product_element):
    wait = WebDriverWait(product_element, 2)
    data = {
        'title': 'N/A',
        'brand': 'N/A',
        'rating': '0',
        'reviews': '0',
        'price': 'N/A',
        'image_url': 'N/A',
        'product_url': 'N/A'
    }

    try:
        # Extract Title
        try:
            data['title'] = wait.until(EC.presence_of_element_located((By.XPATH, ".//h2//span"))).text.strip()
        except (NoSuchElementException, TimeoutException):
            data['title'] = 'N/A'

        # Extract Brand
        try:
            brand_element = product_element.find_element(By.XPATH, ".//span[contains(text(), 'Brand')]/following-sibling::span")
            if brand_element:
                data['brand'] = brand_element.text.strip()
            else:
                data['brand'] = 'N/A'
        except NoSuchElementException:
            try:
                data['brand'] = product_element.find_element(By.XPATH, ".//a[contains(text(), 'Visit the') and contains(text(), 'Store')]").text.strip()
            except NoSuchElementException:
                data['brand'] = 'N/A'

        # Extract Rating
        try:
            data['rating'] = product_element.find_element(By.XPATH, ".//span[@class='a-icon-alt']").get_attribute('textContent').split()[0]
        except NoSuchElementException:
            data['rating'] = '0'

        # Extract Reviews
        try:
            data['reviews'] = product_element.find_element(By.XPATH, ".//span[@class='a-size-base s-underline-text']").text.replace(',', '')
        except NoSuchElementException:
            data['reviews'] = '0'

        # Extract Price
        try:
            data['price'] = product_element.find_element(By.XPATH, ".//span[@class='a-price-whole']").text.replace(',', '')
        except NoSuchElementException:
            data['price'] = 'N/A'

        # Extract Image URL
        try:
            data['image_url'] = product_element.find_element(By.XPATH, ".//img[@class='s-image']").get_attribute('src')
        except NoSuchElementException:
            data['image_url'] = 'N/A'

        # Extract Product URL
        try:
            data['product_url'] = product_element.find_element(By.XPATH, ".//a[@class='a-link-normal s-no-outline']").get_attribute('href')
        except NoSuchElementException:
            data['product_url'] = 'N/A'

    except Exception as e:
        print(f"Error extracting product data: {e}")

    return data

# Scrape Amazon products from the search URL
def scrape_amazon_products(driver, url):
    driver.get(url)
    time.sleep(random.uniform(2, 5))  # Random delay to mimic human behavior

    products = []

    # Scroll down to load more products
    for _ in range(3):
        scroll_down(driver)

    # Find all sponsored products on the page
    sponsored_products = driver.find_elements(By.XPATH, "//div[contains(@class, 's-result-item') and .//span[contains(text(), 'Sponsored')]]")
    
    for product in sponsored_products:
        product_data = extract_product_data(product)
        products.append([product_data['title'], product_data['brand'], product_data['rating'], product_data['reviews'], product_data['price'], product_data['image_url'], product_data['product_url']])

    return products

# Save the scraped data into a CSV file
def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Brand", "Rating", "Reviews", "Price (₹)", "Image URL", "Product URL"])
        writer.writerows(data)

# Main function to run the scraper
def main():
    driver = setup_driver()
    try:
        search_url = "https://www.amazon.in/s?k=soft+toys"
        products = scrape_amazon_products(driver, search_url)

        if products:
            save_to_csv(products, "amazon_sponsored_soft_toys.csv")
            print(f"✅ Successfully saved {len(products)} products to CSV")
        else:
            print("❌ No products found")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        driver.quit()

# Run the scraper
if __name__ == "__main__":
    main()
