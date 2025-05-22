"""
Scraper Author: Zifei Li, Heavily modified by Nemo Xiong
Incorporates dual collection mode strategy with iterative fetching and saving.
"""

# GLOBAL ENVIRONMENT VARIABLES
# Local or Fission
ENVIRONMENT = "Fission"
# should be set to the directory of the deployarchive folder (absolute path, end with /)
FISSION_DEPLOY_DIR = "/userfunc/deployarchive/"
assert FISSION_DEPLOY_DIR.endswith("/"), "FISSION_DEPLOY_DIR must end with a slash"

# -- Import necessary libraries for scraper --
import praw
import pandas as pd
from datetime import datetime  # Ensure datetime is imported
import os
os.environ["FISSION_ENVIRONMENT"] = "true"
os.environ["FISSION_DEPLOY_DIR"] = FISSION_DEPLOY_DIR
import re
import traceback
from tqdm import tqdm  # For progress bars
from textblob import TextBlob
import nltk
import nltk.downloader
from typing import Dict, List, Optional, Tuple, Union, Any
from sentence_transformers import SentenceTransformer

def download_nltk_resource(resource_name: str) -> None:
    """
    Download NLTK resources if not found in the current environment.
    
    Args:
        resource_name: Name of the NLTK resource to download
    """
    downloader = nltk.downloader.Downloader()
    downloader.download(resource_name)

# Ensure 'vader_lexicon' is available for SentimentIntensityAnalyzer
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    try:
        nltk.data.find("vader_lexicon")
    except LookupError:
        print("NLTK 'vader_lexicon' not found. Attempting to download...")
        download_nltk_resource("vader_lexicon")

from nltk.sentiment.vader import SentimentIntensityAnalyzer
# SSL and urllib.request are removed as per user request.

from locality_resolver import (
    create_location_to_state_mapping,
    resolve_ambiguous_locations,
)

ambiguous_locations, location_pids, location_states = create_location_to_state_mapping(FISSION_DEPLOY_DIR + "/locations_with_pid")

from category_indicator_processor import (
    process_csv,
)  # Assuming this file exists and is correct

# -- END of libraries for scraper --

# -- Import necessary libraries for ElasticSearch and Sentence Transformers --
import ssl
import time
import pandas as pd
import numpy as np
from elasticsearch import Elasticsearch, exceptions as es_exceptions
from elasticsearch.helpers import bulk

# -- END of libraries for ElasticSearch and Sentence Transformers --

if ENVIRONMENT == "Fission":
    # set cwd
    os.chdir("/userfunc/deployarchive/")


# --- START SCRAPER CONFIGURATION ---
# COLLECTION_MODE: "HISTORICAL" for deep collection (run on local machine),
#                  "RECENT" for frequent updates (e.g., FaaS cron job).
COLLECTION_MODE_FISSION = "RECENT"  # Options: "HISTORICAL", "RECENT"
COLLECTION_MODE_LOCAL = "RECENT"  # Options: "HISTORICAL", "RECENT"
COLLECTION_MODE = (
    COLLECTION_MODE_FISSION if ENVIRONMENT == "Fission" else COLLECTION_MODE_LOCAL
)

# Time filters to attempt in HISTORICAL mode for each subreddit.
# Original for full historical: TIME_FILTERS_FOR_HISTORICAL = ["year", "month", "week", "day"]
TIME_FILTERS_FOR_HISTORICAL = [
    "year"
]  # FOR TESTING: Using "day" for faster historical runs. Revert for full collection.
TIME_FILTER_FOR_RECENT = "day"

# Max items PRAW attempts to get per search call (Reddit API limit is ~1000).
SEARCH_LIMIT_PER_CALL = 1000  # Default, can be adjusted if needed

# Output directory for master CSV files and final processed files
OUTPUT_DATA_DIR = "data_collected_by_script"
# --- END SCRAPER CONFIGURATION ---

# Initialize PRAW Reddit instance
# IMPORTANT: Store credentials securely (e.g., environment variables, config file), not hardcoded.
reddit = praw.Reddit(
    client_id="rLicpYDSWGMuaL4t5o1bhw",  # Replace with your actual client_id or load securely
    client_secret="RFdbkbbk52zsQYGJIU4VEzhhhUcs_A",  # Replace with your actual client_secret or load securely
    user_agent="ccc-harvester_v12_user_updates",  # Updated user agent
)

if not os.path.exists(OUTPUT_DATA_DIR):
    os.makedirs(OUTPUT_DATA_DIR)

sid = SentimentIntensityAnalyzer()

location_patterns: dict[str, re.Pattern] = {}
for loc_key in location_states.keys():
    location_patterns[loc_key] = re.compile(
        r"\b" + re.escape(loc_key) + r"\b", re.IGNORECASE
    )

subreddits_to_scan = [
    "australia",
    "AusFinance",
    "AustralianPolitics",
    "AusProperty",
    "AusEcon",
    "AusHENRY",
    "fiaustralia",
    "AusPropertyChat",
    "AusRenters",
    "sydney",
    "melbourne",
    "brisbane",
    "perth",
    "adelaide",
    "canberra",
    "hobart",
    "darwin",
    "newcastle",
    "goldcoast",
    "geelong",
    "wollongong",
    "AustralianSocialism",
    "AustralianGreens",
    "liberalaus",
    "australianlabor",
    "Centrelink",
    "auscorp",
    "carsaustralia",
    "aussiefrugal",
    # no "australiaone"
]


keywords_to_search = [
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
    "mental health australia",
]

comment_keywords_filter = [
    "housing",
    "rent",
    "mortgage",
    "property",
    "immigration",
    "immigrants",
    "migrant",
    "foreign",
    "visa",
    "student",
    "affordability",
    "crisis",
    "stress",
    "mental health",
    "anxiety",
    "depression",
    "cost of living",
    "economic",
    "market",
    "policy",
    "government",
    "interest rate",
    "inflation",
    "wage",
    "income",
    "salary",
    "homelessness",
    "landlord",
    "tenant",
    "lease",
    "apartment",
    "house",
    "suburb",
    "location",
    "price",
    "expensive",
    "cheap",
    "investment",
    "investor",
    "speculator",
    "supply",
    "demand",
]

category_indicators_map = {
    "general housing": [
        "housing",
        "property",
        "affordability",
        "homelessness",
        "living costs",
        "housing market",
        "cost of living",
    ],
    "immigration": [
        "immigration",
        "immigrant",
        "migrant",
        "foreign buyer",
        "visa",
        "international student",
    ],
    "rental": ["rental", "rent", "tenant", "lease", "housing stress"],
    "wage": ["wage", "salary", "income", "financial", "economic", "cost of living"],
    "mental health": [
        "mental health",
        "anxiety",
        "depression",
        "stress",
        "wellbeing",
        "insecurity",
    ],
}

# --- HELPER FUNCTIONS (Sentiment, PID assignment, Category determination) ---


def _process_row_for_post_sentiment_emotion(row_data: pd.Series) -> pd.Series:
    """
    Apply sentiment and emotion analysis to a single post row.
    
    Args:
        row_data: DataFrame row containing post data with title and selftext fields
        
    Returns:
        Series containing sentiment analysis results (sentiment, sentiment_score, 
        sentiment_confidence, basic_emotion)
    """
    title = row_data.get("title", "")
    selftext = row_data.get("selftext", "")
    text_content = f"{title} {selftext}".strip()
    
    if not text_content:
        return pd.Series(
            {
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "sentiment_confidence": 0.0,
                "basic_emotion": "neutral",
            }
        )
    sentiment_result = analyse_sentiment_score(text_content)
    basic_emotion_val = emotion_analysis(
        text_content, sentiment_result.get("sentiment_score", 0.0)
    )
    return pd.Series(
        {
            "sentiment": sentiment_result.get("sentiment", "neutral"),
            "sentiment_score": sentiment_result.get("sentiment_score", 0.0),
            "sentiment_confidence": sentiment_result.get("confidence", 0.0),
            "basic_emotion": basic_emotion_val,
        }
    )


def _assign_loc_pid_to_row(row_data: pd.Series, pids_map: dict) -> str:
    """
    Assign location PID to a row based on location and state fields.
    
    Args:
        row_data: DataFrame row containing location and state fields
        pids_map: Dictionary mapping location names to PIDs
        
    Returns:
        Location PID string or empty string if no match found
    """
    location_val = row_data.get("location")
    state_val = row_data.get("state")
    loc_pid_value = ""
    
    if pd.isna(location_val) or pd.isna(state_val) or not location_val:
        return loc_pid_value
        
    loc_name_lower = (
        location_val.split("|", 1)[0].lower()
        if "|" in location_val
        else location_val.lower()
    )
    
    if not loc_name_lower:
        return loc_pid_value
        
    loc_pid_options = pids_map.get(loc_name_lower, [])
    
    if len(loc_pid_options) == 1:
        loc_pid_value = loc_pid_options[0]
    elif len(loc_pid_options) > 1 and isinstance(state_val, str):
        matching_pids = [
            pid
            for pid in loc_pid_options
            if isinstance(pid, str) and pid.startswith(state_val)
        ]
        if matching_pids:
            loc_pid_value = matching_pids[0]
            
    return loc_pid_value


def _process_row_for_comment_sentiment_emotion(row_data: pd.Series) -> pd.Series:
    """
    Apply sentiment, emotion, and category analysis to a single comment row.
    
    Args:
        row_data: DataFrame row containing comment data with body field
        
    Returns:
        Series containing sentiment analysis and category results
    """
    text_content = str(row_data.get("body", "")).strip()
    
    if not text_content:
        return pd.Series(
            {
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "sentiment_confidence": 0.0,
                "basic_emotion": "neutral",
                "comment_category": None,
            }
        )
        
    sentiment_result = analyse_sentiment_score(text_content)
    basic_emotion_val = emotion_analysis(
        text_content, sentiment_result.get("sentiment_score", 0.0)
    )
    comment_categories_val = determine_comment_categories(text_content)
    
    return pd.Series(
        {
            "sentiment": sentiment_result.get("sentiment", "neutral"),
            "sentiment_score": sentiment_result.get("sentiment_score", 0.0),
            "sentiment_confidence": sentiment_result.get("confidence", 0.0),
            "basic_emotion": basic_emotion_val,
            "comment_category": ", ".join(comment_categories_val)
            if comment_categories_val
            else None,
        }
    )


# --- Original Functions (or adapted from user's provided logic) ---


def extract_state_from_location(location: str) -> Optional[str]:
    """
    Extract state from a location string (e.g., 'locality|STATE' or unique locality).
    
    Args:
        location: String containing location information
        
    Returns:
        State string if found, None otherwise
    """
    if pd.isna(location) or not location:
        return None
        
    if "(ambiguous locations)" not in location:
        parts = location.split("|")
        if len(parts) == 2:
            return parts[1]
            
        loc_lower = location.lower()
        if loc_lower in location_states:
            state_list = location_states[loc_lower]
            if state_list:
                return state_list[0]
                
    return None


def extract_locations(text: str) -> List[str]:
    """
    Extract and resolve localities mentioned in text.
    
    Args:
        text: Text to search for location mentions
        
    Returns:
        List of unique locations found in the text
    """
    if pd.isna(text) or not text:
        return []
        
    text_lower = text.lower()
    found_locations_set = set()
    
    for loc_key, pattern in location_patterns.items():
        if pattern.search(text_lower):
            resolved_location = (
                resolve_ambiguous_locations(text_lower, loc_key)
                if loc_key in ambiguous_locations
                else loc_key
            )
            found_locations_set.add(resolved_location)
            
    return list(found_locations_set)


def analyse_sentiment_with_vader(text: str) -> Dict[str, Union[str, float]]:
    """
    Analyze sentiment using VADER sentiment analyzer.
    
    Args:
        text: Text content to analyze
        
    Returns:
        Dictionary containing sentiment classification and scores
    """
    if not text or not isinstance(text, str) or text.strip() == "":
        return {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 1.0,
        }
        
    try:
        sentiment_scores = sid.polarity_scores(text)
        compound_score = sentiment_scores["compound"]
        sentiment = "neutral"
        
        if compound_score >= 0.05:
            sentiment = "positive"
        elif compound_score <= -0.05:
            sentiment = "negative"
            
        return {
            "sentiment": sentiment,
            "sentiment_score": compound_score,
            "positive": sentiment_scores["pos"],
            "negative": sentiment_scores["neg"],
            "neutral": sentiment_scores["neu"],
        }
    except Exception:
        return {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 1.0,
        }


def analyse_sentiment_with_textblob(text: str) -> Dict[str, Union[str, float]]:
    """
    Analyze sentiment using TextBlob analyzer.
    
    Args:
        text: Text content to analyze
        
    Returns:
        Dictionary containing sentiment classification, polarity and subjectivity scores
    """
    if not text or not isinstance(text, str) or text.strip() == "":
        return {"sentiment": "neutral", "polarity": 0.0, "subjectivity": 0.0}
        
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        sentiment = "neutral"
        
        if polarity > 0.1:
            sentiment = "positive"
        elif polarity < -0.1:
            sentiment = "negative"
            
        return {
            "sentiment": sentiment,
            "polarity": polarity,
            "subjectivity": subjectivity,
        }
    except Exception:
        return {"sentiment": "error", "polarity": 0.0, "subjectivity": 0.0}


def analyse_sentiment_score(text: str) -> Dict[str, Union[str, float]]:
    """
    Calculate a weighted sentiment score from VADER and TextBlob analyzers.
    
    Args:
        text: Text content to analyze
        
    Returns:
        Dictionary containing combined sentiment classification, score, and confidence
    """
    if not text or not isinstance(text, str) or text.strip() == "":
        return {"sentiment": "neutral", "sentiment_score": 0.0, "confidence": 0.0}
        
    try:
        vader_result = analyse_sentiment_with_vader(text)
        textblob_result = analyse_sentiment_with_textblob(text)
        vader_weight = 0.7
        textblob_weight = 0.3
        vader_score = vader_result.get("sentiment_score", 0.0)
        textblob_polarity = textblob_result.get("polarity", 0.0)
        weighted_score = (
            vader_score * vader_weight + textblob_polarity * textblob_weight
        )
    except Exception:
        weighted_score = 0.0
        
    sentiment = "neutral"
    if weighted_score >= 0.05:
        sentiment = "positive"
    elif weighted_score <= -0.05:
        sentiment = "negative"
        
    return {
        "sentiment": sentiment,
        "sentiment_score": weighted_score,
        "confidence": min(abs(weighted_score) * 2, 0.95),
    }


def emotion_analysis(text: str, sentiment_score: float) -> str:
    """
    Determine basic emotion based on keywords and sentiment score.
    
    Args:
        text: Text content to analyze
        sentiment_score: Pre-calculated sentiment score for the text
        
    Returns:
        Emotion category (anger, fear, joy, sadness, surprise, or neutral)
    """
    EMOTIONS = {
        "anger": [
            "anger", "angry", "furious", "mad", "outrage", "rage", "frustration",
            "irritation", "annoyed", "hate",
        ],
        "fear": [
            "fear", "afraid", "scared", "terrified", "worried", "anxious", "nervous",
            "panic", "dread", "terror",
        ],
        "joy": [
            "happy", "joy", "delighted", "pleased", "glad", "excited", "cheerful",
            "happiness", "enjoy", "love",
        ],
        "sadness": [
            "sad", "unhappy", "depressed", "miserable", "grief", "sorrow",
            "heartbroken", "upset", "disappointed", "regret",
        ],
        "surprise": [
            "surprise", "shocked", "amazed", "astonished", "unexpected", "wow",
            "unbelievable", "startled",
        ],
        "neutral": [],
    }
    
    NEGATION_WORDS = [
        "not", "no", "never", "don't", "doesn't", "isn't", "aren't", "wasn't",
        "weren't", "can't", "cannot", "couldn't", "shouldn't", "won't", "wouldn't",
        "neither", "nor",
    ]
    
    if not text or not isinstance(text, str) or not text.strip():
        return "neutral"
        
    text_lower = text.lower()
    text_with_spaces = f" {text_lower} "

    for negation in NEGATION_WORDS:
        for emotion, keywords in EMOTIONS.items():
            if emotion == "neutral":
                continue
            for keyword in keywords:
                if f" {negation} {keyword} " in text_with_spaces:
                    if emotion == "joy":
                        return "sadness" if sentiment_score > -0.5 else "anger"
                    if emotion in ["sadness", "anger", "fear"]:
                        return "neutral" if sentiment_score < 0.2 else "joy"
                    if emotion == "surprise":
                        return "neutral"

    emotion_mentions = {emotion: 0 for emotion in EMOTIONS if emotion != "neutral"}
    for emotion, keywords in EMOTIONS.items():
        if emotion == "neutral":
            continue
        for keyword in keywords:
            if re.search(r"\b" + re.escape(keyword) + r"\b", text_lower):
                emotion_mentions[emotion] += 1
                break

    dominant_emotion = None
    if emotion_mentions:
        dominant_emotion = max(emotion_mentions, key=emotion_mentions.get, default=None)
        if dominant_emotion and emotion_mentions.get(dominant_emotion, 0) == 0:
            dominant_emotion = None

    if dominant_emotion:
        if dominant_emotion == "joy" and sentiment_score < -0.3:
            return "sadness"
        if dominant_emotion in ["sadness", "anger", "fear"] and sentiment_score > 0.3:
            return "joy"
        return dominant_emotion

    if sentiment_score >= 0.3:
        return "joy"
    if sentiment_score <= -0.5:
        return "anger"
    if sentiment_score <= -0.2:
        return "sadness"
        
    return "neutral"


def determine_post_categories(post_title: str, post_text: str) -> List[str]:
    """
    Determine categories for a post based on title and text content.
    
    Args:
        post_title: Post title text
        post_text: Post body text
        
    Returns:
        List of category names that apply to the post
    """
    title_str = str(post_title) if pd.notna(post_title) else ""
    text_str = str(post_text) if pd.notna(post_text) else ""
    full_content = (title_str + " " + text_str).lower()
    
    if not full_content.strip():
        return []

    categories = []
    for category, indicators in category_indicators_map.items():
        for indicator in indicators:
            if indicator.lower() in full_content:
                categories.append(category)
                break
                
    return categories


def determine_comment_categories(comment_text: str) -> List[str]:
    """
    Determine categories for a comment based on its text.
    
    Args:
        comment_text: Comment text content
        
    Returns:
        List of category names that apply to the comment
    """
    if pd.isna(comment_text) or not isinstance(comment_text, str):
        return []
        
    comment_text_lower = comment_text.lower()
    
    if not comment_text_lower.strip():
        return []

    categories = []
    for category, indicators in category_indicators_map.items():
        for indicator in indicators:
            if indicator.lower() in comment_text_lower:
                categories.append(category)
                break
                
    return categories


# --- CORE DATA COLLECTION & PROCESSING FUNCTIONS ---


def search_raw_posts(
    subreddit_name_str: str, 
    keyword_query_str: str, 
    time_filter_to_use: str, 
    limit_val: int
) -> pd.DataFrame:
    """
    Core PRAW search function to fetch raw posts based on search parameters.
    
    Args:
        subreddit_name_str: Subreddit name to search in
        keyword_query_str: Search query string
        time_filter_to_use: Time filter value (day, week, month, year)
        limit_val: Maximum number of posts to fetch
        
    Returns:
        DataFrame containing raw post data
    """
    target_subreddit_obj = reddit.subreddit(subreddit_name_str)
    raw_posts_list = []
    tqdm_desc = f"r/{subreddit_name_str} q='{keyword_query_str[:20]}...' tf={time_filter_to_use}"
    
    try:
        for post in tqdm(
            target_subreddit_obj.search(
                keyword_query_str,
                limit=limit_val,
                time_filter=time_filter_to_use,
                sort="new",
            ),
            desc=tqdm_desc,
            leave=False,
            unit="post",
        ):
            post_selftext = post.selftext if post.selftext is not None else ""
            title_locations = extract_locations(post.title)
            text_locations = extract_locations(post_selftext)
            flair_locations = []
            author_flair = getattr(post, "author_flair_text", None)
            if author_flair:
                flair_locations = extract_locations(author_flair)
            all_post_locations = list(
                set(title_locations + text_locations + flair_locations)
            )

            raw_posts_list.append(
                {
                    "title": post.title,
                    "score": post.score,
                    "id": post.id,
                    "url": post.url,
                    "created_utc": datetime.fromtimestamp(post.created_utc),
                    "num_comments": post.num_comments,
                    "author": str(post.author),
                    "selftext": post_selftext,
                    "subreddit": str(post.subreddit.display_name),
                    "is_original_content": post.is_original_content,
                    "upvote_ratio": post.upvote_ratio,
                    "search_query_keyword": keyword_query_str,
                    "search_time_filter": time_filter_to_use,
                    "author_flair_text": author_flair,
                    "locations_mentioned": ", ".join(all_post_locations)
                    if all_post_locations
                    else None,
                }
            )
    except Exception as e_search:
        print(
            f"ERROR during PRAW search (r/{subreddit_name_str}, q='{keyword_query_str}', tf='{time_filter_to_use}'): {e_search}"
        )
        
    return pd.DataFrame(raw_posts_list)


def analyse_raw_posts_df(input_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply sentiment and emotion analysis to a DataFrame of raw posts.
    
    Args:
        input_df: DataFrame containing raw post data
        
    Returns:
        DataFrame with sentiment and emotion analysis columns added
    """
    if input_df.empty:
        return input_df.copy()
        
    analysed_df = input_df.copy()
    
    for col_name in [
        "sentiment",
        "sentiment_score",
        "sentiment_confidence",
        "basic_emotion",
    ]:
        if col_name not in analysed_df.columns:
            if col_name in ["sentiment_score", "sentiment_confidence"]:
                analysed_df[col_name] = 0.0
            else:
                analysed_df[col_name] = "neutral"

    if not analysed_df.empty:
        analysed_df["title"] = analysed_df.get(
            "title", pd.Series(index=analysed_df.index, dtype=str)
        ).fillna("")
        analysed_df["selftext"] = analysed_df.get(
            "selftext", pd.Series(index=analysed_df.index, dtype=str)
        ).fillna("")

        analysis_results = analysed_df.apply(
            _process_row_for_post_sentiment_emotion, axis=1
        )
        analysed_df[
            ["sentiment", "sentiment_score", "sentiment_confidence", "basic_emotion"]
        ] = analysis_results
        
    return analysed_df


def process_posts_for_details(input_df: pd.DataFrame, pids_map: dict) -> pd.DataFrame:
    """
    Process posts for category, location details, and PIDs.
    
    Args:
        input_df: DataFrame containing post data to process
        pids_map: Dictionary mapping location names to PIDs
        
    Returns:
        DataFrame with processed location details, categories, and standardized columns
    """
    output_cols = [
        "post_id",
        "text",
        "created_utc",
        "category",
        "sentiment_score",
        "basic_emotion",
        "location",
        "loc_pid",
        "state",
        "subreddit",
        "search_query_keyword",
        "search_time_filter",
        "url",
        "score",
        "num_comments",
        "author",
        "author_flair_text",
    ]
    
    if input_df.empty:
        return pd.DataFrame(columns=output_cols)

    df_copy = input_df.copy()

    def determine_categories_for_row(row_data: pd.Series) -> str:
        post_title = row_data.get("title", "")
        post_text = row_data.get("selftext", "")
        return ", ".join(determine_post_categories(post_title, post_text))

    df_copy["category"] = df_copy.apply(determine_categories_for_row, axis=1)

    df_copy["text"] = (
        df_copy.get("title", "").astype(str).fillna("")
        + " "
        + df_copy.get("selftext", "").astype(str).fillna("")
    ).str.strip()

    if (
        "locations_mentioned" not in df_copy.columns
        or df_copy["locations_mentioned"].isnull().all()
    ):
        df_copy["location"] = None
        df_copy["loc_pid"] = None
        df_copy["state"] = None
    else:
        loc_series_for_split = df_copy["locations_mentioned"].astype(str).fillna("")
        df_copy["locations_mentioned_list"] = loc_series_for_split.str.split(", ")

        exploded_df = df_copy.explode("locations_mentioned_list")

        if "locations_mentioned_list" in exploded_df.columns:
            exploded_df = exploded_df.rename(
                columns={"locations_mentioned_list": "location"}
            ).reset_index(drop=True)

            exploded_df["location"] = (
                exploded_df["location"].astype(str).fillna("").str.strip()
            )
            exploded_df = exploded_df[exploded_df["location"] != ""]

            if not exploded_df.empty:
                exploded_df["state"] = exploded_df["location"].apply(
                    extract_state_from_location
                )
                exploded_df["loc_pid"] = exploded_df.apply(
                    lambda row: _assign_loc_pid_to_row(row, pids_map), axis=1
                )
                exploded_df = exploded_df[
                    exploded_df["loc_pid"].notna() & (exploded_df["loc_pid"] != "")
                ]
                df_copy = exploded_df
            else:
                df_copy["location"] = None
                df_copy["loc_pid"] = None
                df_copy["state"] = None
                if "locations_mentioned_list" in df_copy.columns:
                    df_copy = df_copy.drop(columns=["locations_mentioned_list"])
        else:
            df_copy["location"] = None
            df_copy["loc_pid"] = None
            df_copy["state"] = None

    if df_copy.empty:
        return pd.DataFrame(columns=output_cols)

    df_copy = df_copy.rename(columns={"id": "post_id"}, errors="ignore")

    df_copy = df_copy.loc[:, ~df_copy.columns.duplicated(keep="first")]

    for col in output_cols:
        if col not in df_copy.columns:
            df_copy[col] = None

    return df_copy.reindex(columns=output_cols)


def get_post_comments_original(
    post_id_val: str, 
    filter_keywords_list: Optional[List[str]] = None, 
    limit_val: Optional[int] = None
) -> pd.DataFrame:
    """
    Fetch comments for a single post ID.
    
    Args:
        post_id_val: Reddit post ID
        filter_keywords_list: Optional list of keywords to filter comments
        limit_val: Maximum number of comment threads to fetch
        
    Returns:
        DataFrame containing comments data
    """
    submission = reddit.submission(id=post_id_val)
    try:
        submission.comments.replace_more(limit=limit_val)
        comments_data = []
        
        for comment in submission.comments.list():
            try:
                comment_text = getattr(comment, "body", "")
                if filter_keywords_list:
                    if not any(
                        keyword.lower() in comment_text.lower()
                        for keyword in filter_keywords_list
                    ):
                        continue

                comment_locations = extract_locations(comment_text)
                flair_locations = []
                author_flair = getattr(comment, "author_flair_text", None)
                if author_flair:
                    flair_locations = extract_locations(author_flair)
                all_comment_locations = list(set(comment_locations + flair_locations))

                comments_data.append(
                    {
                        "id": comment.id,
                        "post_id": post_id_val,
                        "author": str(comment.author),
                        "score": comment.score,
                        "body": comment_text,
                        "created_utc": datetime.fromtimestamp(comment.created_utc),
                        "parent_id": comment.parent_id,
                        "is_submitter": comment.is_submitter,
                        "depth": comment.depth,
                        "author_flair_text": author_flair,
                        "locations_mentioned": ", ".join(all_comment_locations)
                        if all_comment_locations
                        else None,
                        "subreddit_from_post": str(submission.subreddit.display_name),
                        "search_query_keyword_post": submission.title,
                        "search_time_filter_post": "comment_fetch",
                    }
                )
            except Exception as e_comment:
                print(
                    f"Error processing comment {getattr(comment, 'id', 'UNKNOWN')} for post {post_id_val}: {e_comment}"
                )
        return pd.DataFrame(comments_data)
    except Exception as e_submission:
        print(f"Error obtaining comments for post {post_id_val}: {e_submission}")
        return pd.DataFrame()


def get_comments_for_posts_df(
    posts_input_df: pd.DataFrame, 
    filter_keywords_list: Optional[List[str]] = None, 
    comment_limit_val: Optional[int] = None
) -> pd.DataFrame:
    """
    Fetch comments for multiple posts in a DataFrame.
    
    Args:
        posts_input_df: DataFrame containing posts to fetch comments for
        filter_keywords_list: Optional list of keywords to filter comments
        comment_limit_val: Maximum number of comment threads to fetch per post
        
    Returns:
        DataFrame with all fetched comments
    """
    if posts_input_df.empty:
        return pd.DataFrame()
        
    all_comments_list = []

    id_col_name_in_posts_df = "id"
    if id_col_name_in_posts_df not in posts_input_df.columns:
        print(
            f"Warning: Expected post ID column '{id_col_name_in_posts_df}' not found in posts_input_df for comment fetching."
        )
        return pd.DataFrame()

    post_context_map = {}
    for _, post_row in posts_input_df.iterrows():
        post_context_map[post_row[id_col_name_in_posts_df]] = {
            "locations_mentioned": post_row.get("locations_mentioned", ""),
            "subreddit": post_row.get("subreddit", ""),
            "search_query_keyword": post_row.get("search_query_keyword", ""),
            "search_time_filter": post_row.get("search_time_filter", ""),
            "category": post_row.get("category", ""),
        }

    for post_id_val in tqdm(
        posts_input_df[id_col_name_in_posts_df].tolist(),
        desc="Fetching Comments",
        leave=False,
        unit="post",
    ):
        comments_df = get_post_comments_original(
            post_id_val,
            filter_keywords_list=filter_keywords_list,
            limit_val=comment_limit_val,
        )
        if not comments_df.empty:
            post_context = post_context_map.get(post_id_val, {})
            if "locations_mentioned" not in comments_df.columns:
                comments_df["locations_mentioned"] = None

            loc_fill_value = post_context.get("locations_mentioned")
            comments_df["locations_mentioned"] = comments_df[
                "locations_mentioned"
            ].fillna(value=loc_fill_value if loc_fill_value is not None else "")

            comments_df["subreddit"] = post_context.get(
                "subreddit", comments_df.get("subreddit_from_post", "")
            )
            comments_df["search_query_keyword_post"] = post_context.get(
                "search_query_keyword", comments_df.get("search_query_keyword_post", "")
            )
            comments_df["search_time_filter_post"] = post_context.get(
                "search_time_filter", comments_df.get("search_time_filter_post", "")
            )
            comments_df["category_from_post"] = post_context.get("category", "")
            comments_df.drop(
                columns=["subreddit_from_post"], inplace=True, errors="ignore"
            )

            all_comments_list.append(comments_df)
            
    return (
        pd.concat(all_comments_list, ignore_index=True)
        if all_comments_list
        else pd.DataFrame()
    )


def batch_analyse_comments_with_emotion(
    df: pd.DataFrame, 
    batch_size: int = 50
) -> pd.DataFrame:
    """
    Apply sentiment, emotion, and category analysis to comments in batches.
    
    Args:
        df: DataFrame containing comments to analyze
        batch_size: Number of comments to process in each batch
        
    Returns:
        DataFrame with sentiment and category analysis added
    """
    if df.empty:
        return df.copy()
        
    for col_name in [
        "sentiment",
        "sentiment_score",
        "sentiment_confidence",
        "basic_emotion",
        "comment_category",
    ]:
        if col_name not in df.columns:
            if col_name in ["sentiment_score", "sentiment_confidence"]:
                df[col_name] = 0.0
            elif col_name == "comment_category":
                df[col_name] = None
            else:
                df[col_name] = "neutral"

    processed_dfs = []
    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i : i + batch_size].copy()
        if not batch_df.empty:
            batch_df["body"] = batch_df.get(
                "body", pd.Series(index=batch_df.index, dtype=str)
            ).fillna("")
            analysis_results = batch_df.apply(
                _process_row_for_comment_sentiment_emotion, axis=1
            )
            batch_df[
                [
                    "sentiment",
                    "sentiment_score",
                    "sentiment_confidence",
                    "basic_emotion",
                    "comment_category",
                ]
            ] = analysis_results
        processed_dfs.append(batch_df)
        
    return pd.concat(processed_dfs, ignore_index=True) if processed_dfs else df.copy()


def analyse_comment_details(
    df: pd.DataFrame, 
    local_location_pids_map: dict
) -> pd.DataFrame:
    """
    Process comment DataFrame for location details and standardize column structure.
    
    Args:
        df: DataFrame containing comment data to process
        local_location_pids_map: Dictionary mapping location names to PIDs
        
    Returns:
        DataFrame with processed location details and standardized columns
    """
    output_cols = [
        "comment_id",
        "comment_text",
        "created_utc",
        "category",
        "sentiment_score",
        "basic_emotion",
        "location",
        "loc_pid",
        "state",
        "subreddit",
        "post_id_original",
        "search_query_keyword_post",
        "search_time_filter_post",
    ]
    
    if df.empty:
        return pd.DataFrame(columns=output_cols)

    df_copy = df.copy()
    df_copy["final_category"] = df_copy.get(
        "comment_category", pd.Series(index=df_copy.index, dtype=object)
    ).fillna(
        df_copy.get("category_from_post", pd.Series(index=df_copy.index, dtype=object))
    )

    if (
        "locations_mentioned" not in df_copy.columns
        or df_copy["locations_mentioned"].isnull().all()
    ):
        df_copy["location"] = None
        df_copy["loc_pid"] = None
        df_copy["state"] = None
    else:
        loc_series_for_split = df_copy["locations_mentioned"].astype(str).fillna("")
        df_copy["locations_mentioned_list"] = loc_series_for_split.str.split(", ")
        exploded_df = df_copy.explode("locations_mentioned_list")

        if "locations_mentioned_list" in exploded_df.columns:
            exploded_df = exploded_df.rename(
                columns={"locations_mentioned_list": "location"}
            ).reset_index(drop=True)
            exploded_df["location"] = (
                exploded_df["location"].astype(str).fillna("").str.strip()
            )
            exploded_df = exploded_df[exploded_df["location"] != ""]
            if not exploded_df.empty:
                exploded_df["state"] = exploded_df["location"].apply(
                    extract_state_from_location
                )
                exploded_df["loc_pid"] = exploded_df.apply(
                    lambda row: _assign_loc_pid_to_row(row, local_location_pids_map),
                    axis=1,
                )
                exploded_df = exploded_df[
                    exploded_df["loc_pid"].notna() & (exploded_df["loc_pid"] != "")
                ]
                df_copy = exploded_df
            else:
                original_cols = list(df_copy.columns)
                if "locations_mentioned_list" in original_cols:
                    original_cols.remove("locations_mentioned_list")
                df_copy_temp = df_copy.iloc[0:0].reindex(columns=original_cols)
                df_copy_temp["location"] = None
                df_copy_temp["loc_pid"] = None
                df_copy_temp["state"] = None
                df_copy = df_copy_temp
        else:
            df_copy["location"] = None
            df_copy["loc_pid"] = None
            df_copy["state"] = None

    if df_copy.empty:
        return pd.DataFrame(columns=output_cols)

    df_copy = df_copy.rename(
        columns={
            "id": "comment_id",
            "body": "comment_text",
            "final_category": "category",
            "post_id": "post_id_original",
        },
        errors="ignore",
    )
    
    if "location" not in df_copy.columns and "locations_mentioned" in df_copy.columns:
        df_copy = df_copy.rename(columns={"locations_mentioned": "location"})
    elif "location" not in df_copy.columns:
        df_copy["location"] = None

    df_copy = df_copy.loc[:, ~df_copy.columns.duplicated(keep="first")]

    for col in output_cols:
        if col not in df_copy.columns:
            df_copy[col] = None
            
    return df_copy.reindex(columns=output_cols)


def append_to_csv(
    df_to_append: pd.DataFrame, 
    file_path: str, 
    df_type_for_log: str = "data"
) -> None:
    """
    Append a DataFrame to a CSV file, writing header if file doesn't exist.
    
    Args:
        df_to_append: DataFrame to append to the CSV file
        file_path: Path to the CSV file
        df_type_for_log: Type descriptor for log messages
    """
    if df_to_append is None or df_to_append.empty:
        return
        
    file_exists = os.path.isfile(file_path)
    try:
        df_to_append.to_csv(file_path, mode="a", header=not file_exists, index=False)
    except Exception as e_csv:
        print(f"ERROR writing to CSV {file_path}: {e_csv}")


def fetch_and_process_comments(
    posts_df_for_comments: pd.DataFrame, 
    pids_map: dict
) -> pd.DataFrame:
    """
    Fetch, analyze, and process comments for a DataFrame of posts.
    
    Args:
        posts_df_for_comments: DataFrame containing posts to fetch comments for
        pids_map: Dictionary mapping location names to PIDs
        
    Returns:
        DataFrame with processed comment data
    """
    if posts_df_for_comments.empty:
        return pd.DataFrame()

    comments_raw_df = get_comments_for_posts_df(
        posts_df_for_comments, comment_keywords_filter, comment_limit_val=None
    )
    if comments_raw_df.empty:
        return pd.DataFrame()

    comments_analysed_df = batch_analyse_comments_with_emotion(comments_raw_df)

    id_col_in_posts_df = "id"

    if (
        "category" in posts_df_for_comments.columns
        and id_col_in_posts_df in posts_df_for_comments.columns
    ):
        if "post_id" in comments_analysed_df.columns:
            comments_analysed_df = pd.merge(
                comments_analysed_df,
                posts_df_for_comments[[id_col_in_posts_df, "category"]],
                left_on="post_id",
                right_on=id_col_in_posts_df,
                how="left",
                suffixes=("", "_from_post_context"),
            )
            
            if "category_from_post_context" in comments_analysed_df.columns:
                comments_analysed_df["category_from_post"] = comments_analysed_df[
                    "category_from_post_context"
                ]
                cols_to_drop_after_merge = [
                    col
                    for col in comments_analysed_df.columns
                    if "_from_post_context" in col
                    or col == id_col_in_posts_df + "_y"
                    or col == id_col_in_posts_df + "_x"
                ]
                comments_analysed_df.drop(
                    columns=cols_to_drop_after_merge, inplace=True, errors="ignore"
                )
            elif "category" in comments_analysed_df.columns:
                comments_analysed_df["category_from_post"] = comments_analysed_df[
                    "category"
                ]
        else:
            print(
                "Warning: 'post_id' column missing in comments_analysed_df, cannot merge post category for fallback."
            )
            comments_analysed_df["category_from_post"] = None

    final_comment_details_df = analyse_comment_details(comments_analysed_df, pids_map)
    return final_comment_details_df


def fetch_and_process_single_batch(
    subreddit_name: str,
    keyword_query: str,
    time_filter_setting: str,
    pids_map: dict,
    search_limit: int
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Fetch and process one batch of posts and their comments.
    
    Args:
        subreddit_name: Subreddit name to search in
        keyword_query: Search query string
        time_filter_setting: Time filter value
        pids_map: Dictionary mapping location names to PIDs
        search_limit: Maximum number of posts to fetch
        
    Returns:
        Tuple of (processed posts DataFrame, processed comments DataFrame)
    """
    raw_posts_df = search_raw_posts(
        subreddit_name, keyword_query, time_filter_setting, search_limit
    )
    if raw_posts_df.empty:
        return None, None

    analysed_posts_df = analyse_raw_posts_df(raw_posts_df)

    processed_posts_batch = process_posts_for_details(
        analysed_posts_df.copy(), pids_map
    )

    comments_details_batch = None
    if processed_posts_batch is not None and not processed_posts_batch.empty:
        posts_for_comment_fetching = analysed_posts_df[
            analysed_posts_df["id"].isin(processed_posts_batch["post_id"])
        ].copy()

        if not posts_for_comment_fetching.empty:
            if "category" not in posts_for_comment_fetching.columns:
                def determine_cat_for_row(row_data: pd.Series) -> str:
                    return ", ".join(
                        determine_post_categories(
                            row_data.get("title", ""), row_data.get("selftext", "")
                        )
                    )

                posts_for_comment_fetching["category"] = (
                    posts_for_comment_fetching.apply(determine_cat_for_row, axis=1)
                )

            comments_details_batch = fetch_and_process_comments(
                posts_for_comment_fetching, pids_map
            )

    return processed_posts_batch, comments_details_batch


def scrape_main() -> None:
    """
    Main function to control Reddit data collection based on configured mode.
    Fetches posts and comments, analyzes sentiment, extracts locations, and saves to CSV files.
    """
    master_posts_filepath = os.path.join(
        OUTPUT_DATA_DIR, "master_all_posts_details.csv"
    )
    master_comments_filepath = os.path.join(
        OUTPUT_DATA_DIR, "master_all_comments_details.csv"
    )

    if (
        COLLECTION_MODE == "HISTORICAL"
        and os.environ.get("FRESH_HISTORICAL_RUN") == "TRUE"
    ):
        print("FRESH_HISTORICAL_RUN: Clearing existing master CSV files.")
        if os.path.exists(master_posts_filepath):
            os.remove(master_posts_filepath)
        if os.path.exists(master_comments_filepath):
            os.remove(master_comments_filepath)

    time_filters_to_iterate = (
        TIME_FILTERS_FOR_HISTORICAL
        if COLLECTION_MODE == "HISTORICAL"
        else [TIME_FILTER_FOR_RECENT]
    )
    print(
        f"Running in {COLLECTION_MODE} mode. Output Dir: {OUTPUT_DATA_DIR}. Time filters: {time_filters_to_iterate}"
    )

    for subreddit_name in tqdm(
        subreddits_to_scan, desc="Overall Subreddits Progress", unit="subreddit"
    ):
        for tf_value in tqdm(
            time_filters_to_iterate,
            desc=f"r/{subreddit_name} Time Filters",
            leave=False,
            unit="tf",
        ):
            for kw_query in tqdm(
                keywords_to_search,
                desc=f"r/{subreddit_name} ({tf_value}) Keywords",
                leave=False,
                unit="kw",
            ):
                try:
                    processed_posts_df, processed_comments_df = (
                        fetch_and_process_single_batch(
                            subreddit_name,
                            kw_query,
                            tf_value,
                            location_pids,
                            SEARCH_LIMIT_PER_CALL,
                        )
                    )
                    if processed_posts_df is not None and not processed_posts_df.empty:
                        append_to_csv(
                            processed_posts_df, master_posts_filepath, "posts"
                        )
                    if (
                        processed_comments_df is not None
                        and not processed_comments_df.empty
                    ):
                        append_to_csv(
                            processed_comments_df, master_comments_filepath, "comments"
                        )

                except Exception as e_inner_loop:
                    print(
                        f"ERROR in main processing loop (r/{subreddit_name}, kw='{kw_query}', tf='{tf_value}'): {e_inner_loop}"
                    )
                    traceback.print_exc()
        print(f"--- Finished all processing for r/{subreddit_name} ---")

    print(
        "\nAll iterations complete. Attempting final consolidation of master CSV files..."
    )

    final_merged_df_parts = []

    all_possible_final_cols = [
        "content_id",
        "text",
        "created_utc",
        "category",
        "sentiment_score",
        "basic_emotion",
        "location",
        "loc_pid",
        "state",
        "subreddit",
        "search_query_keyword",
        "search_time_filter",
        "url",
        "score",
        "num_comments",
        "author",
        "author_flair_text",
    ]

    if os.path.exists(master_posts_filepath):
        try:
            posts_master_df = pd.read_csv(master_posts_filepath, low_memory=False)
            if not posts_master_df.empty:
                posts_master_df["data_type"] = "post"
                posts_master_df = posts_master_df.rename(
                    columns={"post_id": "content_id"}, errors="ignore"
                )
                final_merged_df_parts.append(posts_master_df)
            else:
                print(f"Master posts file '{master_posts_filepath}' is empty.")
        except pd.errors.EmptyDataError:
            print(
                f"Master posts file '{master_posts_filepath}' is empty (EmptyDataError)."
            )
        except Exception as e_read_posts:
            print(
                f"Error reading/processing master posts file '{master_posts_filepath}': {e_read_posts}"
            )
    else:
        print(f"Master posts file '{master_posts_filepath}' not found.")

    if os.path.exists(master_comments_filepath):
        try:
            comments_master_df = pd.read_csv(master_comments_filepath, low_memory=False)
            if not comments_master_df.empty:
                comments_master_df["data_type"] = "comment"
                comments_master_df = comments_master_df.rename(
                    columns={
                        "comment_id": "content_id",
                        "comment_text": "text",
                        "search_query_keyword_post": "search_query_keyword",
                        "search_time_filter_post": "search_time_filter",
                    },
                    errors="ignore",
                )
                final_merged_df_parts.append(comments_master_df)
            else:
                print(f"Master comments file '{master_comments_filepath}' is empty.")
        except pd.errors.EmptyDataError:
            print(
                f"Master comments file '{master_comments_filepath}' is empty (EmptyDataError)."
            )
        except Exception as e_read_comments:
            print(
                f"Error reading/processing master comments file '{master_comments_filepath}': {e_read_comments}"
            )
    else:
        print(f"Master comments file '{master_comments_filepath}' not found.")

    if final_merged_df_parts:
        standardized_dfs_for_final_concat = []
        for df_part in final_merged_df_parts:
            if df_part.empty:
                continue
            for col_to_ensure in all_possible_final_cols:
                if col_to_ensure not in df_part.columns:
                    df_part[col_to_ensure] = None
            standardized_dfs_for_final_concat.append(
                df_part.reindex(columns=all_possible_final_cols)
            )

        if standardized_dfs_for_final_concat:
            final_merged_df = pd.concat(
                standardized_dfs_for_final_concat, ignore_index=True
            )
            print(
                f"Concatenated data. Total rows before final deduplication: {len(final_merged_df)}"
            )

            final_merged_df.drop_duplicates(
                subset=["content_id", "location", "data_type"],
                inplace=True,
                keep="first",
            )
            print(f"Rows after final deduplication: {len(final_merged_df)}")

            merged_csv_path = os.path.join(
                OUTPUT_DATA_DIR, "all_content_merged_final.csv"
            )
            processed_csv_path = os.path.join(
                OUTPUT_DATA_DIR, "all_content_processed_final.csv"
            )

            final_merged_df.to_csv(merged_csv_path, index=False)
            print(f"Saved final merged data to {merged_csv_path}")

            try:
                process_csv(merged_csv_path, processed_csv_path)
                print(
                    f"Final processed CSV (with category indicators) saved to {processed_csv_path}"
                )
            except Exception as e_process_csv:
                print(
                    f"Error during final CSV processing with process_csv: {e_process_csv}"
                )
        else:
            print("No valid dataframes to concatenate for the final merged file.")
    else:
        print("No data collected in master files to merge and process.")

    print("Script finished.")


#!/usr/bin/env python3
"""
Ingest Author: Nemo Xiong
Integrated Ingestion Script: Reads CSV, generates unique IDs,
generates text embeddings, and bulk ingests into Elasticsearch.
(Version 3 - Handles DeprecationWarning for request_timeout)
"""

# --- START INGEST CONFIGURATION ---
# Elasticsearch Connection Details
ES_HOST = "elasticsearch-master.elastic.svc.cluster.local" if ENVIRONMENT == "Fission" else "localhost"
ES_PORT = 9200
ES_USER = "elastic"
ES_PASSWORD = "385n1Y9ROgnjo666oHt9CMu4"

# Index and File Configuration
CSV_FILE_PATH = "data_collected_by_script/all_content_processed_final.csv"
INDEX_NAME = (
    "all_content_processed_vectorized_v3"  # Using a new index name for this version
)

# Embedding Configuration
TEXT_FIELD_FOR_EMBEDDING = "text"
VECTOR_FIELD_NAME_IN_ES = "text_vector"
MODEL_NAME = "BAAI/bge-small-en-v1.5"

# Ingestion Configuration
BATCH_SIZE = 100
BULK_REQUEST_TIMEOUT = 120  # Specific timeout for bulk requests
DRY_RUN = False
VERBOSE = True

VECTOR_DIMENSION = 0  # Will be set after model loading
# --- END INGEST CONFIGURATION ---


def connect_es() -> Elasticsearch:
    """
    Connect to Elasticsearch server using basic_auth and unverified SSL.
    
    Returns:
        Elasticsearch client instance
        
    Raises:
        SystemExit: If connection fails
    """
    print(f"Connecting to Elasticsearch: https://{ES_HOST}:{ES_PORT}")
    try:
        if hasattr(ssl, "_create_unverified_context"):
            ssl._create_default_https_context = ssl._create_unverified_context

        es_conn = Elasticsearch(
            [f"https://{ES_HOST}:{ES_PORT}"],
            basic_auth=(ES_USER, ES_PASSWORD),
            verify_certs=False,
            ssl_show_warn=False,
        )

        ping_status = es_conn.ping()
        print(f"Elasticsearch Ping Successful: {ping_status}")
        if not ping_status:
            print("ERROR: Failed to connect to Elasticsearch. Ping was unsuccessful.")
            exit(1)
        return es_conn
    except Exception as e:
        print(f"ERROR: Could not connect to Elasticsearch: {str(e)}")
        traceback.print_exc()
        exit(1)


def load_embedding_model() -> SentenceTransformer:
    """
    Load the Sentence Transformer model and set global VECTOR_DIMENSION.
    
    Returns:
        SentenceTransformer model instance
        
    Raises:
        SystemExit: If model loading fails
    """
    global VECTOR_DIMENSION
    print(f"Loading sentence embedding model: {MODEL_NAME}...")
    try:
        model = SentenceTransformer(MODEL_NAME)
        VECTOR_DIMENSION = model.get_sentence_embedding_dimension()
        print(f"Model '{MODEL_NAME}' loaded. Vector dimension: {VECTOR_DIMENSION}")
        return model
    except Exception as e:
        print(f"ERROR: Failed to load model '{MODEL_NAME}': {str(e)}")
        traceback.print_exc()
        exit(1)


def create_es_mapping_integrated(es_client_instance: Elasticsearch) -> None:
    """
    Define and create the Elasticsearch mapping for the integrated data.
    
    Args:
        es_client_instance: Elasticsearch client instance
        
    Raises:
        SystemExit: If vector dimension is not set
    """
    if VECTOR_DIMENSION == 0:
        print(
            "ERROR: Vector dimension not set. Model might not have been loaded correctly for mapping."
        )
        exit(1)

    mapping_body = {
        "mappings": {
            "properties": {
                "unique_id": {"type": "keyword"},
                "content_id": {"type": "keyword"},
                TEXT_FIELD_FOR_EMBEDDING: {"type": "text", "analyzer": "standard"},
                "@timestamp": {
                    "type": "date",
                    "format": "yyyy-MM-dd HH:mm:ss||epoch_millis",
                },
                "sentiment_score": {"type": "float"},
                "basic_emotion": {"type": "keyword"},
                "location": {"type": "keyword"},
                "loc_pid": {"type": "keyword"},
                "state": {"type": "keyword"},
                "subreddit": {"type": "keyword"},
                "search_query_keyword": {"type": "keyword"},
                "search_time_filter": {"type": "keyword"},
                "url": {"type": "keyword", "index": False},
                "score": {"type": "float"},
                "num_comments": {"type": "float"},
                "author": {"type": "keyword"},
                "author_flair_text": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 1024}},
                },
                "data_type": {"type": "keyword"},
                "post_id_original": {"type": "keyword"},
                "isGeneralHousing": {"type": "boolean"},
                "isImmigration": {"type": "boolean"},
                "isRental": {"type": "boolean"},
                "isWage": {"type": "boolean"},
                "isMentalHealth": {"type": "boolean"},
                VECTOR_FIELD_NAME_IN_ES: {
                    "type": "dense_vector",
                    "dims": VECTOR_DIMENSION,
                },
            }
        }
    }
    try:
        if not es_client_instance.indices.exists(index=INDEX_NAME):
            print(f"Creating index '{INDEX_NAME}' with mapping...")
            es_client_instance.indices.create(index=INDEX_NAME, body=mapping_body)
            print(f"Index '{INDEX_NAME}' created successfully.")
        else:
            print(
                f"Index '{INDEX_NAME}' already exists. Will attempt to update mapping for new fields if any."
            )
            try:
                es_client_instance.indices.put_mapping(
                    index=INDEX_NAME, properties=mapping_body["mappings"]["properties"]
                )
                print(f"Mapping for '{INDEX_NAME}' potentially updated for new fields.")
            except Exception as e_map_update:
                print(
                    f"Could not update mapping for '{INDEX_NAME}'. This is normal if no new fields or only incompatible changes. Error: {e_map_update}"
                )
    except Exception as e:
        print(
            f"ERROR: Could not create or update mapping for index '{INDEX_NAME}': {str(e)}"
        )
        traceback.print_exc()


def ingest_and_embed_data(
    es_client_instance: Elasticsearch, 
    model: SentenceTransformer
) -> None:
    """
    Read CSV, generate unique IDs and embeddings, and bulk ingest into Elasticsearch.
    
    Args:
        es_client_instance: Elasticsearch client instance
        model: SentenceTransformer model for generating text embeddings
    """
    if not os.path.exists(CSV_FILE_PATH):
        print(f"ERROR: CSV file '{CSV_FILE_PATH}' not found.")
        return

    print(f"Starting data ingestion from '{CSV_FILE_PATH}' into index '{INDEX_NAME}'.")

    processed_rows_total = 0
    ingested_count_total = 0
    error_count_total = 0
    overall_start_time = time.time()

    es_client_for_bulk = es_client_instance.options(
        request_timeout=BULK_REQUEST_TIMEOUT
    )

    try:
        for chunk_df in pd.read_csv(
            CSV_FILE_PATH, chunksize=BATCH_SIZE, encoding="utf-8-sig", low_memory=False
        ):
            batch_start_time = time.time()

            chunk_df = chunk_df.replace(
                {np.nan: None, pd.NaT: None, "NaN": None, "": None}
            )

            if "loc_pid" in chunk_df.columns:
                original_chunk_size = len(chunk_df)
                chunk_df = chunk_df[
                    pd.to_numeric(chunk_df["loc_pid"], errors="coerce").notna()
                    | chunk_df["loc_pid"].astype(str).str.strip().ne("")
                ]
                chunk_df = chunk_df[chunk_df["loc_pid"].notna()]
                if VERBOSE and len(chunk_df) < original_chunk_size:
                    print(
                        f"  Filtered out {original_chunk_size - len(chunk_df)} rows with empty 'loc_pid'."
                    )
            else:
                print(
                    "WARNING: 'loc_pid' column not found in CSV. Cannot filter by it."
                )

            if chunk_df.empty:
                if VERBOSE:
                    print("  Skipping empty or fully filtered chunk.")
                continue

            chunk_df["content_id_str"] = chunk_df["content_id"].astype(str)
            chunk_df["loc_pid_str"] = chunk_df["loc_pid"].astype(str)
            chunk_df["unique_id"] = (
                chunk_df["content_id_str"] + "_" + chunk_df["loc_pid_str"]
            )

            texts_to_embed = chunk_df[TEXT_FIELD_FOR_EMBEDDING].fillna("").tolist()
            embeddings = []
            if texts_to_embed:
                if VERBOSE:
                    print(f"  Generating embeddings for {len(texts_to_embed)} texts...")
                embeddings = model.encode(texts_to_embed, show_progress_bar=False)

            actions = []
            for i, (_, row) in enumerate(chunk_df.iterrows()):
                doc_source = row.to_dict()
                doc_source.pop("content_id_str", None)
                doc_source.pop("loc_pid_str", None)

                if (
                    "created_utc" in doc_source
                    and doc_source["created_utc"] is not None
                ):
                    try:
                        dt_obj = pd.to_datetime(doc_source["created_utc"])
                        doc_source["@timestamp"] = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception as e_date:
                        if VERBOSE:
                            print(
                                f"    Warning: Could not parse date '{doc_source['created_utc']}'. Setting @timestamp to None. Error: {e_date}"
                            )
                        doc_source["@timestamp"] = None
                    doc_source.pop("created_utc")
                elif "@timestamp" not in doc_source:
                    doc_source["@timestamp"] = datetime.utcnow().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                if i < len(embeddings):
                    doc_source[VECTOR_FIELD_NAME_IN_ES] = embeddings[i].tolist()
                else:
                    doc_source[VECTOR_FIELD_NAME_IN_ES] = None

                bool_fields = [
                    "isGeneralHousing",
                    "isImmigration",
                    "isRental",
                    "isWage",
                    "isMentalHealth",
                ]
                for field in bool_fields:
                    if field in doc_source and doc_source[field] is not None:
                        val = str(doc_source[field]).lower()
                        if val in ["true", "1", "1.0"]:
                            doc_source[field] = True
                        elif val in ["false", "0", "0.0"]:
                            doc_source[field] = False
                        else:
                            doc_source[field] = False

                doc_id = doc_source["unique_id"]
                action = {
                    "_op_type": "update",
                    "_index": INDEX_NAME,
                    "_id": doc_id,
                    "doc": doc_source,
                    "doc_as_upsert": True,
                }
                actions.append(action)

            processed_rows_total += len(chunk_df)

            if not DRY_RUN and actions:
                if VERBOSE:
                    print(f"  Bulk ingesting {len(actions)} documents...")
                try:
                    success_count, errors_in_batch = bulk(
                        es_client_for_bulk, actions, raise_on_error=False
                    )
                    ingested_count_total += success_count
                    if errors_in_batch:
                        num_errors = (
                            len(errors_in_batch)
                            if isinstance(errors_in_batch, list)
                            else 1
                        )
                        error_count_total += num_errors
                        print(
                            f"    WARNING: Encountered {num_errors} errors in batch. First few errors: {str(errors_in_batch)[:500]}"
                        )
                    if VERBOSE and success_count > 0:
                        print(
                            f"    Successfully ingested {success_count} documents in this batch."
                        )
                except es_exceptions.ConnectionTimeout:
                    print(
                        "    ERROR: Bulk ingest batch timed out (based on request_timeout)."
                    )
                    error_count_total += len(actions)
                except Exception as e_bulk:
                    print(f"    ERROR: during bulk batch: {e_bulk}")
                    error_count_total += len(actions)
            elif DRY_RUN and actions:
                print(f"  DRY RUN: Would attempt to ingest {len(actions)} documents.")
                ingested_count_total += len(actions)

            batch_duration = time.time() - batch_start_time
            if VERBOSE:
                print(
                    f"  Batch processed in {batch_duration:.2f} seconds. Total rows examined in script: {processed_rows_total}"
                )
                print("-" * 30)

    except pd.errors.EmptyDataError:
        print(f"ERROR: CSV file '{CSV_FILE_PATH}' is empty.")
    except FileNotFoundError:
        print(f"ERROR: CSV file '{CSV_FILE_PATH}' not found.")
    except Exception as e:
        print(
            f"ERROR: An unexpected error occurred while reading/processing CSV: {str(e)}"
        )
        traceback.print_exc()
        return

    overall_duration = time.time() - overall_start_time
    print("\n--- Ingestion Summary ---")
    print(
        f"Total rows processed from CSV (after attempting loc_pid filter): {processed_rows_total}"
    )
    print(f"Attempted to prepare {ingested_count_total} documents for Elasticsearch.")
    print(f"Encountered {error_count_total} errors during ES ingestion operations.")
    print(f"Total ingestion time: {overall_duration:.2f} seconds.")

    if (
        not DRY_RUN
        and ingested_count_total > 0
        and error_count_total < ingested_count_total
    ):
        try:
            es_client_instance.indices.refresh(index=INDEX_NAME)
            print(f"Index '{INDEX_NAME}' refreshed.")
        except Exception as e_refresh:
            print(f"Could not refresh index '{INDEX_NAME}': {e_refresh}")
    elif DRY_RUN:
        print("This was a DRY RUN. No data was actually written to Elasticsearch.")


def ingest_main() -> None:
    """
    Main function to orchestrate ElasticSearch connection, mapping, and ingestion.
    """
    print("Starting integrated ingestion process...")
    es = connect_es()
    model = load_embedding_model()
    create_es_mapping_integrated(es)
    ingest_and_embed_data(es, model)
    print("\nScript finished.")


def main() -> None:
    """
    Main entry point that runs both data scraping and ingestion.
    """
    scrape_main()
    ingest_main()


if __name__ == "__main__":
    main()
