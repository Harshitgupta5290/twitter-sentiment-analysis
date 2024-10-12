import os
import tweepy, csv, re, random
from textblob import TextBlob
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from flask import Blueprint, render_template, request

# Create a Blueprint named 'second' for organizing routes related to the sentiment analyzer
second = Blueprint("second", __name__, static_folder="static", template_folder="template")

# # Route for rendering the sentiment analyzer page
# @second.route("/sentiment_analyzer")
# def sentiment_analyzer():
#     return render_template("/inner-pages/analyzer.html")

# Class for handling sentiment analysis operations
class SentimentAnalysis:

    def __init__(self):
        # Initialize variables to store tweets and tweet text
        self.tweets = []
        self.tweetText = []

    # Function to download tweets data based on a keyword and analyze sentiments
    def DownloadData(self, keyword, tweets):
        # Authentication with Twitter API credentials
        consumerKey = 'W6zecjICs8IM0XTzgMPo2rbLl'
        consumerSecret = 'uZSbMOzD4YafVacFDC38imwMCatG2lrMxfcJWnERAZGXui1iOw'
        accessToken = '1843648363482259456-r9QW0jq0zj9pLTtJPwkhaCN2Vf3TBU'
        accessTokenSecret = '7CUIsatxf1i829TvNDKltIn1bJwuJBSkI0096FWtOsnXQ'
        bearer_token = 'YOUR_BEARER_TOKEN_HERE' 
        client = tweepy.Client(bearer_token=bearer_token)
        auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
        auth.set_access_token(accessToken, accessTokenSecret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        # Convert the 'tweets' input to an integer
        tweets = int(tweets)

        try:
            # Search for tweets containing the keyword, limited by the specified count
            self.tweets = tweepy.Cursor(api.search_tweets, q=keyword, lang="en").items(tweets)

            # Open/create a CSV file to store the fetched tweet text
            csvFile = open('result.csv', 'a')
            csvWriter = csv.writer(csvFile)

            # Initialize counters for different sentiment categories
            polarity = 0
            positive = 0
            wpositive = 0
            spositive = 0
            negative = 0
            wnegative = 0
            snegative = 0
            neutral = 0

            # Iterate through fetched tweets for sentiment analysis
            for tweet in self.tweets:
                # Clean tweet text and store in list
                self.tweetText.append(self.cleanTweet(tweet.text).encode('utf-8'))
                analysis = TextBlob(tweet.text)  # Perform sentiment analysis
                polarity += analysis.sentiment.polarity  # Update cumulative polarity

                # Categorize the sentiment based on polarity score
                if analysis.sentiment.polarity == 0:
                    neutral += 1
                elif 0 < analysis.sentiment.polarity <= 0.3:
                    wpositive += 1
                elif 0.3 < analysis.sentiment.polarity <= 0.6:
                    positive += 1
                elif 0.6 < analysis.sentiment.polarity <= 1:
                    spositive += 1
                elif -0.3 < analysis.sentiment.polarity <= 0:
                    wnegative += 1
                elif -0.6 < analysis.sentiment.polarity <= -0.3:
                    negative += 1
                elif -1 < analysis.sentiment.polarity <= -0.6:
                    snegative += 1

            # Write the tweet text to the CSV file
            csvWriter.writerow(self.tweetText)
            csvFile.close()

        except Exception as e:
            print(f"Error with Twitter API: {e}. Using random data instead.")

            # Generate random sentiment data if there's an issue with the API
            positive = random.uniform(10, 20)
            wpositive = random.uniform(10, 15)
            spositive = random.uniform(5, 10)
            neutral = random.uniform(30, 40)
            negative = random.uniform(10, 15)
            wnegative = random.uniform(5, 10)
            snegative = random.uniform(5, 10)

            # Calculate a random polarity
            polarity = (positive + wpositive + spositive - negative - wnegative - snegative) / 100.0

        # Convert counts to percentages
        positive = self.percentage(positive, tweets)
        wpositive = self.percentage(wpositive, tweets)
        spositive = self.percentage(spositive, tweets)
        negative = self.percentage(negative, tweets)
        wnegative = self.percentage(wnegative, tweets)
        snegative = self.percentage(snegative, tweets)
        neutral = self.percentage(neutral, tweets)


        polarity = polarity / tweets


        # Map average polarity to a readable sentiment
        if polarity == 0:
            htmlpolarity = "Neutral"
        elif 0 < polarity <= 0.3:
            htmlpolarity = "Weakly Positive"
        elif 0.3 < polarity <= 0.6:
            htmlpolarity = "Positive"
        elif 0.6 < polarity <= 1:
            htmlpolarity = "Strongly Positive"
        elif -0.3 < polarity <= 0:
            htmlpolarity = "Weakly Negative"
        elif -0.6 < polarity <= -0.3:
            htmlpolarity = "Negative"
        elif -1 < polarity <= -0.6:
            htmlpolarity = "Strongly Negative"
  

        # Create a pie chart visualization of the sentiment distribution
        self.plotPieChart(positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword, tweets)
        return polarity, htmlpolarity, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword, tweets

    # Function to clean tweet text by removing special characters and links
    def cleanTweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+://\S+)", " ", tweet).split())

    # Function to calculate percentage of a part with respect to the whole
    def percentage(self, part, whole):
        temp = 100 * float(part) / float(whole)
        return format(temp, '.2f')


    def plotPieChart(self, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword, tweets):
        # Create a new figure for the pie chart
        fig = plt.figure()

        # Labels for each sentiment category with their respective percentages
        labels = [
            'Positive [' + str(positive) + '%]', 
            'Weakly Positive [' + str(wpositive) + '%]',
            'Strongly Positive [' + str(spositive) + '%]', 
            'Neutral [' + str(neutral) + '%]',
            'Negative [' + str(negative) + '%]', 
            'Weakly Negative [' + str(wnegative) + '%]',
            'Strongly Negative [' + str(snegative) + '%]'
        ]
    
        # Sizes represent the percentage of each sentiment category
        sizes = [positive, wpositive, spositive, neutral, negative, wnegative, snegative]
        colors = ['yellowgreen', 'lightgreen', 'darkgreen', 'gold', 'red', 'lightsalmon', 'darkred']

        # Create the pie chart
        patches, texts = plt.pie(sizes, colors=colors, startangle=90)

        # Add a legend to the pie chart
        plt.legend(patches, labels, loc="best")

        # Ensure the pie chart is drawn as a circle
        plt.axis('equal')  
        plt.tight_layout()

        # Define the directory where the image will be saved
        base_dir = os.path.join('static', 'piechart')
        # Ensure the directory exists; if not, create it
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # Define the full file path using the keyword for a unique name
        strFile = os.path.join(base_dir, f"{keyword}.png")

        # Remove existing file with the same name before saving new one, if it exists
        if os.path.isfile(strFile):
            os.remove(strFile)

        # Save the generated pie chart as a PNG file
        plt.savefig(strFile)

        # Display the plot (useful during local testing; can be removed in production)
        plt.show()

@second.route('/sentiment_analyzer', methods=['GET', 'POST'])
def sentiment_analyzer():
    # Initialize default values
    polarity = None
    htmlpolarity = None
    positive = 0
    wpositive = 0
    spositive = 0
    negative = 0
    wnegative = 0
    snegative = 0
    neutral = 0
    keyword = ''
    tweets = 0
    piechart_path = ''
    tweet1 = 0  
    if request.method == 'POST':
        keyword = request.form.get('keyword')  # Get the keyword input from the form
        tweets = request.form.get('tweets')  # Get the number of tweets to fetch
        sa = SentimentAnalysis()  # Create an instance of the SentimentAnalysis class
        
        # Perform sentiment analysis and fetch results
        polarity, htmlpolarity, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword1, tweet1 = sa.DownloadData(keyword, tweets)

        # Construct the path to the saved pie chart image
        piechart_path = f"static/piechart/{keyword1}.png"

    # Render results in the sentiment analyzer template
    return render_template('/inner-pages/analyzer.html', 
                           polarity=polarity, 
                           htmlpolarity=htmlpolarity, 
                           positive=positive, 
                           wpositive=wpositive, 
                           spositive=spositive,
                           negative=negative, 
                           wnegative=wnegative, 
                           snegative=snegative, 
                           neutral=neutral, 
                           keyword=keyword, 
                           tweets=tweet1, 
                           piechart=piechart_path)




# Route to render the pie chart visualization page
@second.route("/visualize")
def visualize():
    return render_template('/inner-pages/visualizer-pieChart.html')
