'''
Author: Zifei Li
'''
# Import necessary libraries
# Python Reddit API Wrapper
# Documentation: https://praw.readthedocs.io/en/stable/index.html
# Note: Although we uses Version 7.8.1, the most recent available documentation in the changelog is for V7.7.1.
#       Therefore, we believe that there are no significant updates in V7.8.1 and developed our project based on
#       V7.7.1 documentation.
#       The code runs successfully without any issues.
import praw
# Data processing and storage
import pandas as pd
# Handle TimeStamps, converting UTC to human-readable time
import datetime
# Import operating system functionalities, including create directors and handle file paths
import os
# Use regular expression to validate the location format
import re
# Print detail error infos
import traceback
# Display a progress bar during executing. Waiting for data without a progress bar is painful!
from tqdm import tqdm
# Sentiment analysis
from textblob import TextBlob
# natural language toolkit
import nltk
# nltk download tool
import nltk.downloader
# Create an SSL context that does not verify the server's certificate
import ssl
# Send request according to the SSL
import urllib.request
# Convert category into binary indicator columns
from category_indicator_processor import process_csv
# Change the global default SSL context so that SSL certificates will not be verified
_create_unverified_https_context = ssl._create_unverified_context

# Set it as the global default SSL context
# From now on, any HTTPS request using the default context will not validate certificates
ssl._create_default_https_context = _create_unverified_https_context

# Replace the default SSL handler used by urllib with one that does not verify SSL certificates
urllib.request._opener = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=ssl._create_unverified_context()))

def download_nltk_resource(resource):
    downloader = nltk.downloader.Downloader()
    # Set the SSL context to ignore certificate validation
    downloader._ssl_context = ssl._create_unverified_context()
    downloader.download(resource)

# download "vader_lexicon"
# vader_lexicon is used to analyse sentiment
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    download_nltk_resource('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Create Reddit instance
reddit = praw.Reddit(
    client_id="v689J_fxXAMBPUQ52vUgwg",
    client_secret="nxZDBn0kQr4wr3qeJ4DxV0B8A_-LBw",
    user_agent="Data Analyser",
)

# Create output directory for storing all scraped data
# Note: this is used to verify whether the output format meets our requirements
output_dir = "data for display"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Create a SentimentIntensityAnalyzer instance to evaluate sentiment scores
sid = SentimentIntensityAnalyzer()

# Location_Parsing is a custom module we developed to create a mapping between locality, state, and loc_pid
# It can also resolve ambiguous locality issues, all duplicate localities can be found in 'ambiguous_locations.csv'
from locality_resolver import create_location_to_state_mapping, resolve_ambiguous_locations

'''
ambiguous_locations: a dictionary mapping ambiguous locality names to a list of state codes
location_pids: a dictionary mapping locality names to a list of loc_pids
location_states: a dictionary mapping locality names to a list of state codes
'''
ambiguous_locations, location_pids, location_states = create_location_to_state_mapping()

subreddits = [
    "australia",
    "AusFinance",
    "AustralianPolitics",
    "AusProperty"
]

all_keywords = [
    "housing crisis immigration",
    "cost of living australia",
    "housing affordability",
    "rental crisis mental health",
    "economic anxiety australia",
    "property prices immigration",
    "housing market australia",
    "inflation housing australia",
    "homelessness australia",
    "living costs australia",
    "immigration housing",
    "immigrants blame housing",
    "immigration policy australia",
    "migrants housing crisis",
    "foreign buyers property",
    "visa housing impact",
    "international students rent",
    "immigration australia",
    "rental crisis australia",
    "rent increase australia",
    "housing stress",
    "rental market australia",
    "rental affordability",
    "rental shortage",
    "australia rent expensive",
    "rental prices australia",
    "wage growth australia",
    "salary housing affordability",
    "income housing ratio",
    "wage stagnation australia",
    "cost of living wage",
    "income inequality australia",
    "salary increase australia",
    "wage housing gap",
    "housing stress mental health",
    "rental stress anxiety",
    "cost of living depression",
    "financial stress mental",
    "housing insecurity wellbeing",
    "rent increase anxiety",
    "housing crisis wellbeing",
    "mental health australia"
]

comment_keywords = [
    "housing", "rent", "mortgage", "property", "immigration",
    "immigrants", "migrant", "foreign", "visa", "student",
    "affordability", "crisis", "stress", "mental health",
    "anxiety", "depression", "cost of living", "economic",
    "market", "policy", "government", "interest rate",
    "inflation", "wage", "income", "salary", "homelessness",
    "landlord", "tenant", "lease", "apartment", "house",
    "suburb", "location", "price", "expensive", "cheap",
    "investment", "investor", "speculator", "supply", "demand"
]

category_indicators = {
    "general housing": ["housing", "property", "affordability", "homelessness", "living costs", "housing market", "cost of living"],
    "immigration": ["immigration", "immigrant", "migrant", "foreign buyer", "visa", "international student"],
    "rental": ["rental", "rent", "tenant", "lease", "housing stress"],
    "wage": ["wage", "salary", "income", "financial", "economic", "cost of living"],
    "mental health": ["mental health", "anxiety", "depression", "stress", "wellbeing", "insecurity"]
}

def extract_state_from_location(location):
    """
    Extract the state code from a location

    Args:
        location (str): The location mentioned in a post. Please note that the locations here
                        have been processed by 'resolve_ambiguous_locations', thus only have
                        the following 3 formats:
                        - locality (ambiguous location): Duplicate localities with unknown state
                                                         (cannot resolve state from context)
                        - locality|state: Duplicate localities with resolved state
                        - locality: Unique localities

    Return:
        str: The corresponding state code
    """
    # Only locations without ambiguities are retained
    # We can not handle ambiguous locations effectively currently
    # Therefore, we just remove them
    if "(ambiguous locations)" not in location:
        parts = location.split("|")
        if len(parts) == 2:
            return parts[1]
        else:
            loc_lower = location.lower()
            if loc_lower in location_states:
                state = location_states[loc_lower]
                return state[0]

def extract_locations(text):
    """
    Extract and parse mentioned localities from a text

    Args：
        text (str)：The text from which to extract the localities

    Return：
        list：A list of parsed localities
    """
    text_lower = text.lower()
    found_locations = []

    # We use regex pattern here to ensure an exact match of the locality as a whole word
    # Prevent partial matches within other words
    for location in location_states.keys():
        pattern = r'\b' + re.escape(location) + r'\b'
        if re.search(pattern, text_lower):
            if location in ambiguous_locations:
                resolved_location = resolve_ambiguous_locations(text_lower, location)
            else:
                resolved_location = location
            if resolved_location not in found_locations:
                found_locations.append(resolved_location)

    return found_locations

def search_posts(subreddit, query, limit=100, time_filter="all"):
    """
    Search for posts in a specific subreddit through keywords

    Args:
        subreddit (str): Name of the subreddit
        query (str): Search keyword
        limit (int): Number of posts to retrieve. Here, limit = 100 is set only to verify that
                     the output content and format meet our requirements. We are currently
                     continuously fetching posts from reddit
        time_filter (str): Time filter for search, defaults to "all"

    Return:
        pd.DataFrame: Posts match the search criteria
    """
    subreddit = reddit.subreddit(subreddit)
    search_results = []

    # The 'post' object is an instance of PRAW's Submission class
    # For detailed attributes and methods, you can see the PRAW documentation below:
    # https://praw.readthedocs.io/en/stable/code_overview/models/submission.html
    for post in subreddit.search(query, limit=limit, time_filter=time_filter):
        try:
            title_location = extract_locations(post.title)
            text_location = extract_locations(post.selftext)
            flair_locations = []

            if hasattr(post, 'author_flair_text') and post.author_flair_text is not None:
                flair_locations = extract_locations(post.author_flair_text)

            all_locations = list(set(title_location + text_location + flair_locations))

            search_results.append({
                "title": post.title,
                "score": post.score,
                "id": post.id,
                "url": post.url,
                "created_utc": datetime.datetime.fromtimestamp(post.created_utc),
                "num_comments": post.num_comments,
                "author": str(post.author),
                "selftext": post.selftext,
                "subreddit": str(post.subreddit),
                "is_original_content": post.is_original_content,
                "upvote_ratio": post.upvote_ratio,
                "search_query": query,
                "author_flair_text": post.author_flair_text if hasattr(post, "author_flair_text") else None,
                "locations_mentioned": ", ".join(all_locations) if all_locations else None,
                "post_time_of_day": datetime.datetime.fromtimestamp(post.created_utc).strftime("%H:%M"),
                "post_day_of_week": datetime.datetime.fromtimestamp(post.created_utc).strftime("%A")
            })
        except Exception as e:
            print(f"Error searching post: {e}")

    return pd.DataFrame(search_results)

def search_posts_with_location(subreddit, query, limit=200, time_filter="all"):
    """
    Search posts in a subreddit by keywords and only keep those with locations

        Args:
            subreddit (str): Name of the subreddit
            query (str): Search keyword
            limit (int): Number of posts to retrieve
            time_filter (str): Time filter for search

        Return:
            pd.DataFrame: Posts with locations
    """
    search_results = search_posts(subreddit,query,limit = limit,time_filter=time_filter)

    if search_results.empty:
        return pd.DataFrame()

    location_posts = search_results[search_results['locations_mentioned'].notna()]

    return location_posts

def search_multiple_subreddits_with_location(subreddits, queries, limit=200, time_filter="all"):
    """
    Search posts in multiple subreddits by keywords and only keep those with locations

    Args:
        subreddit (str): Name of the subreddit
        queries (list): Search keyword
        limit (int): Number of posts to retrieve
        time_filter (str): Time filter for search

    Return:
        pd.DataFrame: Posts with locations from all subreddits
    """
    all_results = pd.DataFrame()
    for subreddit in subreddits:
        for query in queries:
            results = search_posts_with_location(subreddit, query, limit=limit, time_filter=time_filter)
            if not results.empty:
                all_results = pd.concat([all_results, results])

    if not all_results.empty:
        all_results = all_results.drop_duplicates(subset=["id"])

    return all_results

def analyse_sentiment_with_vader(text):
    """
    Analyse sentiment using VADER model

    Documentation: https://www.nltk.org/api/nltk.sentiment.vader.html

    Arg:
        text (str): The text to analyse

    Return:
        dict: A dictionary containing the sentiment
    """
    if not text or not isinstance(text, str) or text.strip() == "":
        return {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 0.0
        }

    try:
        sentiment_scores = sid.polarity_scores(text)
        compound_score = sentiment_scores['compound']
        if compound_score >= 0.05:
            sentiment = "positive"
        elif compound_score <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "sentiment_score": compound_score,
            "positive": sentiment_scores['pos'],
            "negative": sentiment_scores['neg'],
            "neutral": sentiment_scores['neu']
        }
    except Exception as e:
        return {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 1.0
        }

def analyse_sentiment_with_textblob(text):
    """
    Analyse sentiment using TextBlob

    Documentation: https://textblob.readthedocs.io/en/dev/

    Arg:
        text (str): The text to analyse

    Return:
        dict: A dictionary containing sentiment
    """
    if not text or not isinstance(text, str) or text.strip() == "":
        return {
            "sentiment": "neutral",
            "polarity": 0.0,
            "subjectivity": 0.0
        }

    try:
        blob = TextBlob(text)

        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        if polarity > 0.1:
            sentiment = "positive"
        elif polarity < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "polarity": polarity,
            "subjectivity": subjectivity
        }
    except Exception as e:
        return {
            "sentiment": "error",
            "polarity": 0.0,
            "subjectivity": 0.0
        }

def analyse_sentiment_score(text):
    """
    Analyse sentiment scores

    Arg:
        text (str): The text to analyse

    Return:
        dict: A dictionary containing sentiment scores
    """
    if not text or not isinstance(text, str) or text.strip() == "":
        return {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
        }
    try:
        vader_result = analyse_sentiment_with_vader(text)
        textblob_result = analyse_sentiment_with_textblob(text)

        # VADER is optimised for social media, giving higher weight
        vader_weight = 0.7
        textblob_weight = 0.3

        weighted_score = (vader_result["sentiment_score"] * vader_weight + textblob_result["polarity"] * textblob_weight)

    except Exception as e:
        weighted_score = 0.0

    if weighted_score >= 0.05:
        sentiment = "positive"
    elif weighted_score <= -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "sentiment": sentiment,
        "sentiment_score": weighted_score,
        # Scaled to make it more sensitive and to better reflect the intensity of sentiment
        "confidence": min(abs(weighted_score) * 2, 0.95)
    }

def batch_analyse_posts_with_emotion(df, batch_size=50):
    """
    Process posts in batches
    Avoid loading too much posts at a time, which could reduce memory efficiency
    Each batch is processed sequentially, not in parallel
    After each batch, the progress bar is updated accordingly

    Args:
        df (pd.DataFrame): A DataFrame containing post data
        batch_size (int): Number of posts to process in each batch

    Return:
        pd.DataFrame: DataFrame containing post data with sentiment and emotions
    """
    if df.empty:
        return df

    df['sentiment'] = None
    df['sentiment_score'] = None
    df['sentiment_confidence'] = None
    df['basic_emotion'] = None

    def process_batch(batch):
        result_batch = batch.copy()
        for index, row in batch.iterrows():
            # Combine 'title' and 'selftext' for analysis
            title = row['title'] if 'title' in row else ""
            selftext = row['selftext'] if 'selftext' in row and row['selftext'] else ""
            text = f"{title} {selftext}"

            sentiment_result = analyse_sentiment_score(text)

            result_batch.at[index, 'sentiment'] = sentiment_result.get('sentiment', 'neutral')
            result_batch.at[index, 'sentiment_score'] = sentiment_result.get('sentiment_score', 0.0)
            result_batch.at[index, 'sentiment_confidence'] = sentiment_result.get('confidence', 0.0)

            basic_emotion = emotion_analysis(text, sentiment_result.get('sentiment_score', 0.0))
            result_batch.at[index, 'basic_emotion'] = basic_emotion

        return result_batch

    with tqdm(total=len(df), desc="sentiment and emotion analysis") as pbar:
        processed_dfs = []

        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size].copy()
            result_batch = process_batch(batch)
            processed_dfs.append(result_batch)
            pbar.update(len(batch))

        result_df = pd.concat(processed_dfs) if processed_dfs else df

    return result_df

def search_multiple_subreddits_with_location_and_scores(subreddits, queries, limit=200, time_filter="all"):
    """
    Search for posts related to keywords with location infos in multiple subreddits

    Args:
        subreddits (list): List of subreddits to search
        queries (list): List of search keywords
        limit (int): Search limit
        time_filter (str): Time filter

    Return:
        pd.DataFrame: Posts data containing locations and sentiment scores
    """
    all_results = search_multiple_subreddits_with_location(subreddits, queries, limit, time_filter)

    if not all_results.empty:
        all_results = batch_analyse_posts_with_emotion(all_results)

    return all_results

def analyse_post_details(df):
    """
    Analyse posts to extract important display information for the frontend

    Arg:
        df (pd.DataFrame): DataFrame containing post data

    Return:
        pd.DataFrame: DataFrame containing selected fields for frontend display
    """
    # Combine 'title' and 'selftext'
    # Note: The 'text' and 'selftext' do not impact our data display
    #       They are used primarily for extracting location information and analysing the poster's sentiment
    #       Therefore, we decided to merge them for storage
    df['text'] = df.apply(
        lambda row: f"{row['title']} {row['selftext']}" if pd.notna(row['selftext']) else row['title'],
        axis=1
    )

    df['locations_mentioned'] = df['locations_mentioned'].str.split(', ')
    exploded_df = df.explode('locations_mentioned')
    exploded_df = exploded_df.reset_index(drop=True)
    exploded_df['state'] = exploded_df['locations_mentioned'].apply(extract_state_from_location)
    exploded_df['loc_pid'] = ""

    for index, row in exploded_df.iterrows():
        location = row['locations_mentioned']
        state = row['state']
        loc_pid = ""

        if "|" in location:
            loc_name, _ = location.split("|")
        else:
            loc_name = location
        loc_pid_values = location_pids.get(loc_name.lower(), [])

        if len(loc_pid_values) == 1:
            loc_pid = loc_pid_values[0]
        else:
            matching_pids = [pid for pid in loc_pid_values if isinstance(pid, str) and pid.startswith(state)]

            if matching_pids:
                loc_pid = matching_pids[0]

        exploded_df.at[index, 'loc_pid'] = loc_pid

    exploded_df = exploded_df[exploded_df['loc_pid'].notna() & (exploded_df['loc_pid'] != "")]

    result_df = exploded_df[['id', 'text', 'created_utc', 'category', 'sentiment_score','basic_emotion',
                             'locations_mentioned', 'loc_pid', 'state']].copy()
    result_df.columns = ['post_id', 'text', 'created_utc', 'category', 'sentiment_score', 'basic_emotion',
                         'location', 'loc_pid', 'state']

    return result_df

def process_search_results(post_df,):
    """
    Process search results and save necessary data

    Arg:
        post_df (pd.DataFrame): The search results

    Return:
        pd.DataFrame: DataFrame containing selected fields for frontend display
    """
    if not post_df.empty:
        post_details = analyse_post_details(post_df)

        return post_details
    else:
        return None

def determine_post_categories(post_title, post_text):
    '''
    Determine relevant categories for a given post based on keyword indicator

    Args:
        post_title (str): The title of the post
        post_text (str): the selftext of the post

    Return:
        list: A list of matched categories
    '''
    full_content = (post_title + " " + post_text).lower()
    categories = []

    for category, indicators in category_indicators.items():
        for indicator in indicators:
            if indicator.lower() in full_content:
                categories.append(category)
                break

    return categories

def emotion_analysis(text, sentiment_score):
    """
    Analyse emotion according to emotion keywords and sentiment score

    Args:
        text (str): The text to analyse
        sentiment_score (float): The sentiment score of the text

    Return:
        str: The dominant emotion for the text
    """
    EMOTIONS = {
        "anger": ["anger", "angry", "furious", "mad", "outrage", "rage", "frustration", "irritation", "annoyed",
                  "hate"],
        "fear": ["fear", "afraid", "scared", "terrified", "worried", "anxious", "nervous", "panic", "dread", "terror"],
        "joy": ["happy", "joy", "delighted", "pleased", "glad", "excited", "cheerful", "happiness", "enjoy", "love"],
        "sadness": ["sad", "unhappy", "depressed", "miserable", "grief", "sorrow", "heartbroken", "upset",
                    "disappointed", "regret"],
        "surprise": ["surprise", "shocked", "amazed", "astonished", "unexpected", "wow", "unbelievable", "startled"],
        "neutral": []
    }

    NEGATION_WORDS = ["not", "no", "never", "don't", "doesn't", "isn't", "aren't", "wasn't", "weren't",
                      "can't", "cannot", "couldn't", "shouldn't", "won't", "wouldn't", "neither", "nor"]

    if not text or not isinstance(text, str):
        return "neutral"

    text_lower = text.lower()
    # Avoid misjudgments at the beginning of a sentence (e.g., "Not happy ...")
    text_with_spaces = f" {text_lower}"

    # Handle combinations of negation words and emotion words first
    # Note: This logic comes from our team members' daily life
    #       It's not 100% complete or perfect - just a rough guide that works okay in most cases
    for negation in NEGATION_WORDS:
        for emotion, keywords in EMOTIONS.items():
            # Negated neutral emotions are ambiguous
            # They can be either positive or negative
            # Therefore, we choose not to classify them
            if emotion == "neutral":
                continue

            for keyword in keywords:
                if f" {negation} {keyword}" in text_with_spaces:
                    # Negated positive emotions are usually negative
                    if emotion == "joy":
                        return "sadness" if sentiment_score > -0.5 else "anger"

                    # Negated negative emotions are usually not necessarily positive, they can also be neutral
                    if emotion in ["sadness", "anger", "fear"]:
                        return "neutral" if sentiment_score < 0.2 else "joy"

                    # Negated surprise is likely neutral
                    if emotion == "surprise":
                        return "neutral"

    # Check for explicit emotion words
    emotion_mentions = {}
    for emotion, keywords in EMOTIONS.items():
        if emotion == "neutral":
            continue

        emotion_mentions[emotion] = 0
        for keyword in keywords:
            # Ensure the keywords can be recognised correctly whether it appears in the middle or the end of the text
            patterns = [f" {keyword} ", f" {keyword}.", f" {keyword},",
                        f" {keyword}!", f" {keyword}?", f" {keyword}\n",
                        f" {keyword}:", f" {keyword};", f"{keyword} "]

            for pattern in patterns:
                if pattern in text_with_spaces:
                    emotion_mentions[emotion] += 1
                    break

    # We believe a person can only have one dominant emotion at any time
    # It's hard to imagine someone felling happy and sad at the same time
    max_mentions = 0
    dominant_emotion = None

    for emotion, count in emotion_mentions.items():
        if count > max_mentions:
            max_mentions = count
            dominant_emotion = emotion

    # When any words from the dominant_emotion category appear:
    # Note: Similar to above, these rules are derived from our daily life
    #       It's not 100% complete or perfect - just a rough guide that works okay in most cases
    if dominant_emotion and max_mentions > 0:
        # Verify if the sentiment score matches the detected emotion
        # We consider that some people might use sarcasm to express their opinion
        if dominant_emotion == "joy" and sentiment_score < -0.3:
            return "sadness"
        elif dominant_emotion in ["sadness", "anger", "fear"] and sentiment_score > 0.3:
            return "joy"
        else:
            return dominant_emotion

    # If no clear emotion words are found, then use the sentiment score
    if sentiment_score >= 0.3:
        return "joy"
    elif sentiment_score <= -0.5:
        return "anger"
    elif sentiment_score <= -0.2:
        return "sadness"
    elif sentiment_score >= 0.15:
        return "surprise"
    else:
        return "neutral"

def get_post_comments(post_id, keywords=None, limit=None):
    '''
    Retrieve comments from a specific Reddit post

    Args:
        post_id (str): The ID of the Reddit post
        keywords (list): Comment keywords
        limit: Search limit

    Return:
        pd.DataFrame: A DataFrame containing comment information (structured consistently with the post data)
    '''
    submission = reddit.submission(id=post_id)
    try:
        submission.comments.replace_more(limit=limit)
        comments_data = []
        for comment in submission.comments.list():
            try:
                comment_text = comment.body if hasattr(comment, "body") else ""
                if keywords:
                    comment_text_lower = comment_text.lower()
                    if not any(keyword.lower() in comment_text_lower for keyword in keywords):
                        continue
                comment_locations = extract_locations(comment_text)
                flair_locations = []
                if hasattr(comment, "author_flair_text") and comment.author_flair_text:
                    flair_locations = extract_locations(comment.author_flair_text)

                all_locations = list(set(comment_locations + flair_locations))

                comments_data.append({
                    "id": comment.id,
                    "post_id": post_id,
                    "author": str(comment.author),
                    "score": comment.score,
                    "body": comment.body,
                    "created_utc": datetime.datetime.fromtimestamp(comment.created_utc),
                    "parent_id": comment.parent_id,  # Parent comment ID (for tracking comment hierarchy)
                    "is_submitter": comment.is_submitter,
                    "depth": comment.depth,
                    "author_flair_text": comment.author_flair_text if hasattr(comment, "author_flair_text") else None,
                    "locations_mentioned": ", ".join(all_locations) if all_locations else None,
                    "comment_time_of_day": datetime.datetime.fromtimestamp(comment.created_utc).strftime("%H:%M"),
                    "comment_day_of_week": datetime.datetime.fromtimestamp(comment.created_utc).strftime("%A")
                })
            except Exception as e:
                print(f"Error in processing comments {e}")
        return pd.DataFrame(comments_data)
    except Exception as e:
        print(f"Error in obtaining comments {e}")
        return pd.DataFrame()

def get_comments_for_posts(post_df, keywords=None, comment_limit=None):
    '''
    Retrieve comments from multiple Reddit posts

    Args:
        post_df (pd.DataFrame): DataFrame containing multiple Reddit posts
        keywords (list): Search keywords
        comment_limit (int): Search limit

    Return:
        pd.DataFrame: A DataFrame containing comment information from all posts
    '''
    all_comments = pd.DataFrame()
    post_locations = {}
    for index, post in post_df.iterrows():
        post_id = post["id"]
        locations = post.get("locations_mentioned")
        if isinstance(locations, list):
            locations = ", ".join(locations)
        post_locations[post_id] = locations

    for post_id in post_df['id'].tolist():
        comments = get_post_comments(post_id, keywords, limit=comment_limit)

        if not comments.empty:
            for index, comment in comments.iterrows():
                if pd.isna(comments.at[index, 'locations_mentioned']):
                    comments.at[index, 'locations_mentioned'] = post_locations.get(post_id)
            all_comments = pd.concat([all_comments, comments])

    return all_comments

def batch_analyse_comments_with_emotion(df, batch_size=50):
    '''
    Process comments in batches

    Args:
        df (pd.DataFrame): A DataFrame containing comment data
        batch_size (int): Number of posts to process per batch

    Return:
        pd.DataFrame: DataFrame containing comment data with sentiment and emotion
    '''
    if df.empty:
        return df

    df['sentiment'] = None
    df['sentiment_score'] = None
    df['sentiment_confidence'] = None
    df['basic_emotion'] = None

    def process_batch(batch):
        result_batch = batch.copy()
        for index, row in batch.iterrows():
            text = row['body'] if 'body' in row and row['body'] else ""
            sentiment_result = analyse_sentiment_score(text)
            result_batch.at[index, 'sentiment'] = sentiment_result.get('sentiment', 'neutral')
            result_batch.at[index, 'sentiment_score'] = sentiment_result.get('sentiment_score', '0.0')
            result_batch.at[index, 'sentiment_confidence'] = sentiment_result.get('sentiment_confidence', '0.0')

            basic_emotion = emotion_analysis(text, sentiment_result.get('sentiment_score', '0.0'))
            result_batch.at[index, 'basic_emotion'] = basic_emotion

            comment_categories = determine_comment_categories(text)
            result_batch.at[index, 'comment_category'] = ", ".join(comment_categories) if comment_categories else None
        return result_batch

    with tqdm(total=len(df), desc="Comment sentiment analysis") as pbar:
        processed_dfs = []
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size].copy()
            result_batch = process_batch(batch)
            processed_dfs.append(result_batch)
            pbar.update(len(batch))

        result_df = pd.concat(processed_dfs) if processed_dfs else df

    return result_df


def determine_comment_categories(comment_text):
    '''
    Determine relevant categories for a given comment based on keyword indicator

    Arg:
        comment_text: The comment text to analyse

    Return:
        list: A list of matched categories
    '''
    comment_text_lower = comment_text.lower()
    categories = []

    for category, indicators in category_indicators.items():
        for indicator in indicators:
            if indicator.lower() in comment_text_lower:
                categories.append(category)
                break

    return categories

def analyse_post_details_for_comments(df):
    """
    Analyse comments to extract important display information for the frontend

    Args:
        df (pd.DataFrame): DataFrame containing comment data

    Return:
        DataFrame: DataFrame containing selected fields for frontend display
    """
    if df.empty:
        return None

    df['category'] = df['comment_category'].fillna(df.get('category', ''))
    df['locations_mentioned'] = df['locations_mentioned'].str.split(', ')
    exploded_df = df.explode('locations_mentioned')
    exploded_df = exploded_df.reset_index(drop=True)
    exploded_df['state'] = exploded_df['locations_mentioned'].apply(extract_state_from_location)
    exploded_df['loc_pid'] = ""

    for index, row in exploded_df.iterrows():
        location = row['locations_mentioned']
        state = row['state']
        loc_pid = ""
        if "|" in location:
            loc_name, _ = location.split("|")
        else:
            loc_name = location
        loc_pid_values = location_pids.get(loc_name.lower(), [])

        if len(loc_pid_values) == 1:
            loc_pid = loc_pid_values[0]
        else:
            matching_pids = [pid for pid in loc_pid_values if isinstance(pid, str) and pid.startswith(state)]

            if matching_pids:
                loc_pid = matching_pids[0]

        exploded_df.at[index, 'loc_pid'] = loc_pid

    exploded_df = exploded_df[exploded_df['loc_pid'].notna() & (exploded_df['loc_pid'] != "")]

    result_df = exploded_df[['id', 'body', 'created_utc', 'category', 'sentiment_score', 'basic_emotion',
                             'locations_mentioned', 'loc_pid', 'state']].copy()
    result_df.columns = ['comment_id', 'comment_text', 'created_utc', 'category', 'sentiment_score',
                         'basic_emotion', 'location', 'loc_pid', 'state']

    return result_df

def main():

    all_posts_data = []
    all_comments_data = []

    try:
        for keyword in all_keywords:
            try:
                search_results = search_multiple_subreddits_with_location_and_scores(subreddits, [keyword], limit = 200, time_filter = "all")

                if not search_results.empty:
                    for index, post in search_results.iterrows():
                        post_title = post["title"]
                        post_text = post["selftext"] if "selftext" in post else None

                        categories = determine_post_categories(post_title, post_text)

                        if categories:
                            post_copy = post.copy()
                            post_copy['category'] = ", ".join(categories)
                            post_df = pd.DataFrame([post_copy])
                            post_details = process_search_results(post_df)

                            if post_details is not None:
                                all_posts_data.append(post_details)

                                comments = get_comments_for_posts(post_df, comment_keywords, comment_limit = None)

                                if not comments.empty:
                                    comments = batch_analyse_comments_with_emotion(comments)

                                    comment_details = analyse_post_details_for_comments(comments)
                                    if comment_details is not None:
                                        all_comments_data.append(comment_details)
            except Exception as e:
                print(f"Error searching for keyword '{keyword}': {e}")
                traceback.print_exc()
    except Exception as e:
        print("Error during search process:")
        traceback.print_exc()

    if all_posts_data and all_comments_data:
        all_posts_df = pd.concat(all_posts_data)
        all_posts_df = all_posts_df.drop_duplicates(subset=['post_id', 'location'])

        all_posts_df['data_type'] = 'post'

        all_posts_df = all_posts_df.rename(columns={
            'post_id': 'content_id',
            'text': 'content_text'
        })

        all_comments_df = pd.concat(all_comments_data)
        all_comments_df = all_comments_df.drop_duplicates(subset=['comment_id', 'location'])

        all_comments_df['data_type'] = 'comment'

        all_comments_df = all_comments_df.rename(columns={
            'comment_id': 'content_id',
            'comment_text': 'content_text'
        })

        columns_to_use = ['content_id', 'content_text', 'created_utc', 'category',
                          'sentiment_score', 'basic_emotion', 'location', 'loc_pid',
                          'state', 'data_type']

        merged_df = pd.concat([
            all_posts_df[columns_to_use],
            all_comments_df[columns_to_use]
        ])

        merged_df.to_csv(f"{output_dir}/all_content_merged.csv", index=False)
        all_posts_df.to_csv(f"{output_dir}/all_posts_details.csv", index=False)
        all_comments_df.to_csv(f"{output_dir}/all_comments_details.csv", index=False)
        process_csv(f"{output_dir}/all_content_merged.csv", f"{output_dir}/all_content_processed.csv")
    else:
        if all_posts_data:
            all_posts_df = pd.concat(all_posts_data)
            all_posts_df = all_posts_df.drop_duplicates(subset=['post_id', 'location'])
            all_posts_df.to_csv(f"{output_dir}/all_posts_details.csv", index=False)
            process_csv(f"{output_dir}/all_posts_details.csv", f"{output_dir}/all_posts_processed.csv")

        if all_comments_data:
            all_comments_df = pd.concat(all_comments_data)
            all_comments_df = all_comments_df.drop_duplicates(subset=['comment_id', 'location'])
            all_comments_df.to_csv(f"{output_dir}/all_comments_details.csv", index=False)
            process_csv(f"{output_dir}/all_comments_details.csv", f"{output_dir}/all_comments_processed.csv")

if __name__ == "__main__":
    main()