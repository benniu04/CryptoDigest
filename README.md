# CryptoDigest 🗞

## Description ✏️

CryptoDigest is an automated system designed to keep the user informed about the latest news in the crypto world. This Python-based tool scrapes cryptocurrency news articles, more specifically Bitcoin-related ones, summarizes them for quick consumption, stores them in a MongoDB database for future access, and sends out daily digest emails with summaries to me.

# Example Email

<img width="1132" alt="news-examples" src="https://github.com/benniu04/CryptoDigest/assets/138111756/6626078a-cedf-483b-a37c-ff7c70368a11">


## Features 💥

Automated News Scraping: Daily scraping of the latest cryptocurrency news from Yahoo Finance and related sources

NLP Summarization: Use the T5 transformer and SimplyT5 models to condense articles into digestible summaries.

Database Storage: News summaries, titles, and URLs are stored in a MongoDB database, allowing for data analysis and retrieval.

Daily Email Digests: Users of the script can receive a daily email with the latest news summaries when running the script

## Installation 🛠

To set up CryptoDigest, follow these steps:

## Clone the repository:

⚡ git clone https://github.com/yourusername/CryptoDigest.git

⚡ cd CryptoDigest

⚡ install the required library packages

## Set up environment variables for MongoDB and email configuration by adding them to your .bashrc or .bash_profile:

⚡ export MONGO_URI="your_mongodb_uri"

⚡ export SENDER_EMAIL="your_email@example.com"

⚡ export RECEIVER_EMAIL="receiver_email@example.com"

⚡ export EMAIL_PASSWORD="your_email_password"

⚡ before running the training.py script, ensure you have a dataset ready to train the model.

## Contributing ⭐️

Contributions make the open-source community an amazing place to learn, inspire, and create. Any contributions to extend the sources, improve summarization, or enhance email formatting are greatly appreciated.

## Fork the project 🍴

⚡ Create your Feature Branch (git checkout -b feature/NewFeature)

⚡ Commit your changes (git commit -m 'Add some NewFeature')

⚡ Push to the Branch (git push origin feature/NewFeature)

⚡ Open a Pull Request

## Important Notes ⚠️

⚡ If I had more time to work on this project, I would incorporate more data to further fine-tune the model and generate more precise summaries. The summaries generated are mostly correct but grammar and capitalization can be improved.

⚡ The training_data-_actual.csv file is my own collected data, the user can have their CSV file with their data to train their model.

⚡ The test.py file is for testing and messing with the training parameters of the model to see how different values can influence the output of summaries.

## License 🪪

This project is licensed under the GPL-2.0 License - see the LICENSE.md file for details.

## Acknowledgments 🍁

Special thanks to the creators of the T5 model and the BeautifulSoup library for enabling the core functionalities of this project.
