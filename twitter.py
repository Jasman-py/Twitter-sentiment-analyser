import re
import tweepy
from textblob import TextBlob
import matplotlib.pyplot as plt

def authenticate_twitter(api_key, api_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)

def clean_tweet(text):
    text = re.sub(r'^RT @\w+: ', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'http\S+', '', text)
    return text.strip()

def adjust_for_negation(text, polarity):
    negations = ["not", "no", "never", "n't"]
    positive_words = ["good", "happy", "great", "excellent", "amazing", "love"]
    lowered = text.lower()
    for neg in negations:
        for pos_word in positive_words:
            if f"{neg} {pos_word}" in lowered:
                return -abs(polarity)
    return polarity

def analyze_tweets(api, search, tweet_amount):
    positive, negative, neutral, polarity = 0, 0, 0, 0
    tweets = tweepy.Cursor(api.search_tweets, q=search, lang="en", tweet_mode="extended").items(tweet_amount)
    for tweet in tweets:
        text = tweet.full_text if hasattr(tweet, "full_text") else tweet.text
        text = clean_tweet(text)
        analysis = TextBlob(text)
        score = adjust_for_negation(text, analysis.sentiment.polarity)
        if score > 0:
            positive += 1
        elif score == 0:
            neutral += 1
        else:
            negative += 1
        polarity += score
    avg_polarity = polarity / tweet_amount if tweet_amount > 0 else 0
    return positive, negative, neutral, avg_polarity

def visualize_results(positive, negative, neutral):
    labels = ["Positive", "Negative", "Neutral"]
    sizes = [positive, negative, neutral]
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140, shadow=True)
    plt.title("Twitter Sentiment Analysis")
    plt.show()

if __name__ == "__main__":
    api_key = input("Enter your API key here: ")
    api_secret = input("Enter your API secret here: ")
    access_token = input("Enter your access token here: ")
    access_token_secret = input("Enter your access token secret here: ")
    api = authenticate_twitter(api_key, api_secret, access_token, access_token_secret)
    search = input("Enter search term here: ")
    tweet_amount = int(input("Enter number of tweets to analyze: "))
    positive, negative, neutral, avg_polarity = analyze_tweets(api, search, tweet_amount)
    print("\n--- Sentiment Analysis Results ---")
    print(f"Positive Tweets: {positive}")
    print(f"Negative Tweets: {negative}")
    print(f"Neutral Tweets: {neutral}")
    print(f"Average Polarity: {avg_polarity:.2f}")
    visualize_results(positive, negative, neutral)
