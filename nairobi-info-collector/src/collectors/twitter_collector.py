"""Twitter/X data collector using the Twitter API."""

from typing import List, Optional
from datetime import datetime, timedelta
import os

from .base_collector import BaseCollector
from src.models import InformationItem, ReliabilityLevel, Category


class TwitterCollector(BaseCollector):
    """
    Collector for Twitter/X data.

    Note: Requires Twitter API credentials in environment variables.
    """

    def __init__(self):
        """Initialize Twitter collector."""
        super().__init__("Twitter/X", ReliabilityLevel.MEDIUM)

        # API credentials
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_secret = os.getenv('TWITTER_ACCESS_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

        self.client = None

        # Initialize API client if credentials are available
        if self.bearer_token:
            self._init_client()

    def _init_client(self):
        """Initialize Twitter API client."""
        try:
            import tweepy

            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_secret,
                wait_on_rate_limit=True
            )

            self.logger.info("Twitter API client initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter client: {e}")
            self.client = None

    def collect(self, query: str = "Nairobi", limit: int = 50) -> List[InformationItem]:
        """
        Collect tweets about Nairobi.

        Args:
            query: Search query
            limit: Maximum number of tweets to collect

        Returns:
            List of InformationItem objects
        """
        if not self.client:
            self.logger.warning("Twitter client not initialized. Skipping collection.")
            return []

        self.logger.info(f"Collecting tweets for query: {query}")

        items = []

        try:
            import tweepy

            # Enhanced query with Nairobi-specific terms
            search_query = f"{query} (Nairobi OR Kenya OR #Nairobi OR #NairobiCity) -is:retweet lang:en"

            # Search recent tweets
            tweets = self.client.search_recent_tweets(
                query=search_query,
                max_results=min(limit, 100),
                tweet_fields=['created_at', 'public_metrics', 'entities', 'geo'],
                expansions=['author_id'],
                user_fields=['username', 'verified']
            )

            if not tweets.data:
                self.logger.info("No tweets found")
                return []

            # Create user lookup dict
            users = {user.id: user for user in tweets.includes.get('users', [])} if tweets.includes else {}

            for tweet in tweets.data:
                try:
                    # Get tweet author
                    author = users.get(tweet.author_id)
                    username = author.username if author else "unknown"
                    is_verified = author.verified if author else False

                    # Extract metrics
                    metrics = tweet.public_metrics
                    likes = metrics.get('like_count', 0)
                    retweets = metrics.get('retweet_count', 0)
                    replies = metrics.get('reply_count', 0)

                    # Create title from username and preview
                    tweet_preview = tweet.text[:50] + "..." if len(tweet.text) > 50 else tweet.text
                    title = f"@{username}: {tweet_preview}"

                    # Extract hashtags
                    hashtags = []
                    if tweet.entities and 'hashtags' in tweet.entities:
                        hashtags = [tag['tag'] for tag in tweet.entities['hashtags']]

                    # Determine category based on content
                    category = self._categorize_tweet(tweet.text, hashtags)

                    # Create item
                    item = self.create_information_item(
                        title=title,
                        summary=tweet.text,
                        category=category,
                        source_url=f"https://twitter.com/{username}/status/{tweet.id}",
                        timestamp=tweet.created_at,
                        tags=hashtags,
                        metadata={
                            'platform': 'twitter',
                            'author': username,
                            'verified': is_verified,
                            'likes': likes,
                            'retweets': retweets,
                            'replies': replies,
                            'engagement': likes + retweets + replies
                        }
                    )

                    items.append(item)

                except Exception as e:
                    self.logger.warning(f"Error processing tweet: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error collecting tweets: {e}")

        # Filter and deduplicate
        items = self.filter_relevant_items(items)
        items = self.deduplicate_items(items)

        self.logger.info(f"Collected {len(items)} relevant tweets")
        return items

    def collect_trending_hashtags(self, location_id: int = 1528488) -> List[str]:
        """
        Collect trending hashtags for Nairobi.

        Args:
            location_id: WOEID for Nairobi (default: 1528488)

        Returns:
            List of trending hashtags
        """
        if not self.client:
            return []

        try:
            import tweepy

            # Note: Trends endpoint requires API v1.1
            auth = tweepy.OAuth1UserHandler(
                self.api_key,
                self.api_secret,
                self.access_token,
                self.access_secret
            )
            api_v1 = tweepy.API(auth)

            trends = api_v1.get_place_trends(location_id)

            hashtags = [
                trend['name']
                for trend in trends[0]['trends']
                if trend['name'].startswith('#')
            ]

            self.logger.info(f"Found {len(hashtags)} trending hashtags")
            return hashtags[:10]  # Return top 10

        except Exception as e:
            self.logger.error(f"Error collecting trending hashtags: {e}")
            return []

    def _categorize_tweet(self, text: str, hashtags: List[str]) -> Category:
        """Categorize tweet based on content."""
        text_lower = f"{text} {' '.join(hashtags)}".lower()

        # Check for events
        if any(word in text_lower for word in ['concert', 'festival', 'event', 'exhibition']):
            return Category.CULTURE_EVENTS

        # Check for food/nightlife
        if any(word in text_lower for word in ['food', 'restaurant', 'bar', 'club', 'dining']):
            return Category.FOOD_NIGHTLIFE

        # Check for business
        if any(word in text_lower for word in ['startup', 'business', 'tech', 'innovation']):
            return Category.BUSINESS_ECONOMY

        # Check for transportation
        if any(word in text_lower for word in ['traffic', 'matatu', 'uber', 'road']):
            return Category.TRANSPORTATION

        # Default to social media
        return Category.SOCIAL_MEDIA
