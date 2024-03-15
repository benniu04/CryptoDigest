# Import necessary libraries
from simplet5 import SimpleT5
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import T5Tokenizer
import torch
import os

# Disable parallel tokenization to avoid potential issues on certain platforms
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def main():
    # Initialize the SimpleT5 model
    model = SimpleT5()
    # Load the t5-base model
    model.from_pretrained(model_type="t5", model_name="t5-base")

    # Load training data from local CSV file
    df = pd.read_csv('training_data-_actual.csv', encoding='latin-1', usecols=['Text', 'Target_Text'])
    # Display first 12 rows of the dataset to check for validity
    print(df.head(12))

    # Rename columns for compatibility with SimpleT5 input requirements
    df.rename(columns={'Text': 'source_text', 'Target_Text': 'target_text'}, inplace=True)

    # Prepend each source text with "summarize: " to indicate summarization task
    df['source_text'] = "summarize: " + df['source_text']

    # Split the data into training and testing sets
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

    # Train the model with a subset of the data to avoid memory issues
    model.train(train_df=train_df[:5000],  # first 5000 rows of data are used for training
                eval_df=test_df[:100],  # Use first 100 rows for evaluation
                source_max_token_len=512,  # Max token length for source text
                target_max_token_len=256,  # Max token length for target text
                batch_size=8, max_epochs=5, use_gpu=False)  # Training parameters

    # Load a trained model for inference
    model.load_model("t5", "outputs/simplet5-epoch-4-train-loss-0.3779-val-loss-0.3049", use_gpu=False)

    # Example text to summarize
    text_to_summarize = 'MicroStrategy Inc. Chairman Michael Saylor discussed his views on Bitcoin and how his ' \
                        'company will handle its huge investment going forward during an interview on CNBC. ' \
                        '"We’re buying it to hold it 100 years. So, that being the case, that $66,000 to $16,' \
                        '000 crash. That shook out the tourists. That shook out the nonbelievers. When it was 16,000, ' \
                        'we were all ready to ride it to zero. And that’s what you’ll find with the Bitcoin ' \
                        'maximalists."''Dont Miss: If you invested $100 in DOGE when Elon Musk first tweeted about it ' \
                        'in 2019, here’s how much you’d have today. About 22% of the adult population in the U.S. own ' \
                        'a share of Bitcoin, how much would $10 get you today? MicroStrategy has amassed more than ' \
                        '193,000 tokens over the past several years, making it the largest institutional holder in ' \
                        'the world. At the time of writing, the tokens are worth nearly $14 billion. ' \
                        'Saylor also discussed the differences between buying MicroStrategy shares and some of the ' \
                        'recently approved Bitcoin exchange-traded funds (ETFs). He said that MicroStrategy shares ' \
                        'allow you to hold Bitcoin in an "accretive" manner, as they are using loans to continually ' \
                        'buy more. MicroStrategy recently announced that it was selling $700 million of convertible ' \
                        'notes to buy more tokens. Additionally, Saylor noted that the fees charged by the ETFs, ' \
                        'usually around 0.25%, are unattractive. While this could be a smaller point to Bitcoin ' \
                        'maximalists, or those who simply want exposure to Bitcoin alone, Saylor noted that ' \
                        'MicroStrategy is essentially "giving you a yield on your shares" through its combination of ' \
                        'Bitcoin holdings and business operations. MicroStrategy has performed extremely well, ' \
                        'up over 650% in the past year. However, it is important to note that Saylor is incentivized ' \
                        'to paint MicroStrategy shares in the best way possible, as he holds over 200,000 shares, ' \
                        'worth over $300 million. ' \
                        'Trending: Bitcoin To $100,000? Here’s what gold bug Peter Schiff said could happen on ' \
                        'Anthony Pompliano’s podcast. ' \
                        'Saylor also compared Bitcoin to other assets, such as gold, bonds and real estate, ' \
                        'because it is digital and "you can trade it a million times faster than conventional ' \
                        'assets." He also mentioned that it trades 24/7, is a global currency and that it is ' \
                        'decentralized and useful. ' \
                        'In addition, Saylor mentioned that the halving could be a further benefit to Bitcoin in ' \
                        'terms of price. He says that Bitcoin has "no negative catalysts" because it is decentralized ' \
                        'and doesnt have cash flows. Additionally, he mentioned that the halving could reduce the ' \
                        'amount of selling activity, as the miners would have less BTC to sell each day. According to ' \
                        'Saylor, the halving will reduce the amount of Bitcoin mined each day from 900 to 450. Saylor ' \
                        'also discussed the underlying business operations of MicroStrategy. Though it is a software ' \
                        'company, Saylor said that he is hoping to rebrand as a "Bitcoin development company" that ' \
                        'uses the operating cash flows from the software business to fund more Bitcoin purchases. ' \
                        'Saylor closed the interview by urging viewers not to think of Bitcoin as a currency, ' \
                        'but as "digital property; a billion-dollar building in cyberspace ... the killer application ' \
                        'is capital preservation for everybody." Read Next: ' \
                        'Large boom in cryptocurrency and metaverse interest as BTC skyrockets — has Apple Vision Pro ' \
                        'increased the demand for virtual real estate? ' \
                        'The last-standing top crypto exchange without a major security breach offers what now? ' \
                        '"ACTIVE INVESTORS SECRET WEAPON''Supercharge Your Stock Market Game with the #1 news & ' \
                        'everythingelse trading tool: Benzinga Pro - Click here to start Your 14-Day Trial Now! ""Get ' \
                        'the latest stock analysis from Benzinga?' \
                        'This article Michael Saylor: Bitcoins $66K To $16K Crash … Shook Out The Nonbelievers As ' \
                        'MSTR Is Up 650% In The Past Year originally appeared on Benzinga.com © 2024 Benzinga.com. ' \
                        'Benzinga does not provide investment advice. All rights reserved.'

    # Tokenize the text for input to T5 model
    tokenizer = T5Tokenizer.from_pretrained("t5-base")
    inputs = tokenizer.encode(text_to_summarize, return_tensors="pt", max_length=512, truncation=True)
    truncated_text = tokenizer.decode(inputs[0], skip_special_tokens=True)

    # Generate summary with the loaded model
    summary = model.predict(truncated_text, max_length=512)
    print(summary)

    # Save the state of the model for later
    torch.save(model.model.state_dict(),
               'outputs/simplet5-epoch-4-train-loss-0.3779-val-loss-0.3049/my_model_epoch5_loss0.3779.pth')


# Ensure script runs only when executed directly
if __name__ == '__main__':
    main()
