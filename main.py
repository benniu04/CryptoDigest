# import the necessary libraries
import csv
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urljoin

import certifi
import requests
import torch
import os
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from transformers import T5Tokenizer, T5ForConditionalGeneration
from webdriver_manager.firefox import GeckoDriverManager

# Initialize model for summarization
model_name = "t5-base"
tokenizers = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# Load pre-trained model weights
model_path = 'outputs/simplet5-epoch-4-train-loss-0.3232-val-loss-0.4057/my_model_epoch5_loss0.3232.pth'
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))


# Function to summarize the text using a pre-trained T5 model
def summarize_text(text, min_length, max_length):
    # Preprocess scraped text
    preprocess_text = text.strip().replace("\n", "")
    prepared_text = f"summarize: {preprocess_text}"
    tokenized_text = tokenizers.encode(prepared_text, return_tensors="pt", max_length=512, truncation=True)

    # Generate the summary
    summary_generate = model.generate(tokenized_text, max_length=max_length, min_length=min_length, length_penalty=2.0,
                                      num_beams=20, early_stopping=True, no_repeat_ngram_size=2)  # higher num_beam
    # generates more concise summaries

    # Decode summary
    summary = tokenizers.decode(summary_generate[0], skip_special_tokens=True)
    return summary


# Setup Selenium for web scraping
options = Options()
options.headless = True
service = Service(executable_path=GeckoDriverManager().install())
driver = webdriver.Firefox(options=options, service=service)

# Url to scrape
URL = "https://finance.yahoo.com/topic/crypto/"

# CSV file path
CSV_FILE_PATH = 'revised-article-news.csv'

# MongoDB configurations
MONGO_URI = os.getenv('MONGO_URI')
Database_Name = 'test'
Collection_Name = 'headersAndURL'
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[Database_Name]
collection = db[Collection_Name]

# Email setup
subject = "Daily Crypto News"
sender_email = os.getenv('sender_email')
receiver_email = os.getenv('receiver_email')
password = os.getenv('password')  # use an app password from gmail for security reasons
smtp_server = "smtp.gmail.com"
smtp_port = 587  # TLS


# Function to read existing URLs from a CSV file
def read_existing_urls(file_path):
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            return {row[1] for row in csv.reader(file) if row and len(row) > 1}
    except FileNotFoundError:
        return set()


# Function to read existing headers from a CSV file
def read_existing_headers(file_path):
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            return {row[0] for row in csv.reader(file) if row}
    except FileNotFoundError:
        return set()


# Function to check if an article already exists in the MongoDB collection
def art_exist(url):
    return collection.find_one({'url': url}) is not None


# Initialize to manage existing URLs and headers
existing_urls = read_existing_urls(CSV_FILE_PATH)
existing_headers = read_existing_headers(CSV_FILE_PATH)

# Set user-agent to mimic real browser for scraping
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/58.0.3029.110 Safari/537.3'
}

# Make request to specified URL
page = requests.get(URL)
page.raise_for_status()

# Prepare to write article info to a CSV file
with open('revised-article-news.csv', 'a', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Header', 'URL', 'Content'])

    # Try setup to check if the page is available and has the appropriate status_code
    try:
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'lxml')
            articles = soup.find_all('h3', class_='Mb(5px)')

            articles_info = []

            # Loop through the found articles and processes each one
            for article in articles:
                article_link = article.find('a')
                if article_link and 'bitcoin' in article_link.text.lower():
                    header_text = article_link.text.strip()  # Text of the article
                    link_url = urljoin(URL, article_link['href'])  # URL of the article
                    print(f"Title: {header_text}, URL: {link_url}")
                    csv_writer.writerow([header_text, link_url])
                    existing_urls.add(link_url)  # Add the new URL to the set

                    # Use Selenium for dynamic web pages
                    driver.get(link_url)
                    driver.implicitly_wait(10)  # Wait for the page to load, can be adjusted accordingly
                    newSoup = BeautifulSoup(driver.page_source, 'lxml')
                    content = newSoup.find_all('div', class_='caas-body')
                    actual_content = ''
                    for container in content:
                        paragraphs = container.find_all('p')  # Find all <p> tags within each 'caas-body' container
                        for paragraph in paragraphs:
                            actual_content += paragraph.text + ' '  # Concatenate text from each paragraph
                    actual_content = actual_content.strip()

                    # Summarize the article content
                    if actual_content:
                        new_min_length = 75
                        new_max_length = max(int(len(actual_content) * 0.6), new_min_length)
                        actual_summary = summarize_text(actual_content,
                                                        min_length=new_min_length, max_length=new_max_length)
                        print(actual_summary)
                        articles_info.append({"title": header_text, "url": link_url, "summary": actual_summary})
                        # Save the article info in MongoDB and writes it in the CSV file
                        if not art_exist(link_url):
                            collection.insert_one(
                                {"header": header_text, "url": link_url, "content": actual_summary})
                            csv_writer.writerow([header_text, link_url, actual_summary])
                            body = "Daily Crypto News Summary:\n\n"
                            for art in articles_info:
                                body += f"Title: {art['title']}\nURL: {art['url']}\nSummary:\n{art['summary']}\n\n"
                    else:
                        print("Content not found :(")

            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))

            context = ssl.create_default_context(cafile=certifi.where())

            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls(context=context)
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
                print("Email was sent successfully!")
            except Exception as e:
                print(f"Failed to send email: {e}")
            finally:
                server.quit()

    except Exception as e:
        print("An error has occurred ", str(e))

# Close the Selenium web driver
driver.quit()
