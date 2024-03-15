from urllib.parse import urljoin
import requests
import torch
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from transformers import T5Tokenizer, T5ForConditionalGeneration
from webdriver_manager.firefox import GeckoDriverManager

model_name = "t5-base"
tokenizers = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

model_path = 'outputs/simplet5-epoch-4-train-loss-0.3779-val-loss-0.3049/my_model_epoch5_loss0.3779.pth'
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))


# T5 model
def summarize_text(text, min_length, max_length):
    preprocess_text = text.strip().replace("\n", "")
    t5_prepared_text = f"summarize: {preprocess_text}"

    tokenized_text = tokenizers.encode(t5_prepared_text, return_tensors="pt", max_length=512, truncation=True)

    summary_ids = model.generate(tokenized_text, max_length=max_length, min_length=min_length, length_penalty=2,
                                 num_beams=18, early_stopping=True, no_repeat_ngram_size=2)  # higher num_beam
    # generates more concise summaries

    summary = tokenizers.decode(summary_ids[0], skip_special_tokens=True)

    # clean_summary_text = clean_summary(summary)

    return summary


options = Options()
options.headless = True

service = Service(executable_path=GeckoDriverManager().install())
driver = webdriver.Firefox(options=options, service=service)

URL = "https://finance.yahoo.com/topic/crypto/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/58.0.3029.110 Safari/537.3'
}

page = requests.get(URL)
page.raise_for_status()


try:
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'lxml')
        articles = soup.find_all('h3', class_='Mb(5px)')

        for article in articles:
            article_link = article.find('a')
            if article_link and 'bitcoin' in article_link.text.lower():
                header_text = article_link.text.strip()  # Text of the article
                link_url = urljoin(URL, article_link['href'])  # URL of the article
                print(f"Title: {header_text}, URL: {link_url}")
                driver.get(link_url)
                driver.implicitly_wait(10)
                newSoup = BeautifulSoup(driver.page_source, 'lxml')
                content = newSoup.find_all('div', class_='caas-body')
                actual_content = ''
                for container in content:
                    paragraphs = container.find_all('p')  # Find all <p> tags within each 'caas-body' container
                    for paragraph in paragraphs:
                        actual_content += paragraph.text + ' '  # Concatenate text from each paragraph
                actual_content = actual_content.strip()

                if actual_content:
                    new_min_length = 75
                    new_max_length = max(int(len(actual_content) * 0.5), new_min_length)
                    actual_summary = summarize_text(actual_content, min_length=new_min_length, max_length=
                    new_max_length)
                    print(actual_summary)

                else:
                    print("Content not found :(")


except Exception as e:
    print("An error has occurred ", str(e))

driver.quit()
