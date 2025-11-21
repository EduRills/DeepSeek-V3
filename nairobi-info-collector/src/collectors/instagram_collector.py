"""Instagram data collector."""

from typing import List, Optional
from datetime import datetime
import os

from .base_collector import BaseCollector
from src.models import InformationItem, ReliabilityLevel, Category


class InstagramCollector(BaseCollector):
    """
    Collector for Instagram data.

    Note: Uses instagrapi library for data collection.
    Requires Instagram credentials in environment variables.
    """

    def __init__(self):
        """Initialize Instagram collector."""
        super().__init__("Instagram", ReliabilityLevel.MEDIUM)

        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')

        self.client = None

        if self.username and self.password:
            self._init_client()

    def _init_client(self):
        """Initialize Instagram API client."""
        try:
            from instagrapi import Client

            self.client = Client()
            # Note: Uncomment when credentials are available
            # self.client.login(self.username, self.password)

            self.logger.info("Instagram client initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize Instagram client: {e}")
            self.client = None

    def collect(self, query: str = "Nairobi", limit: int = 50) -> List[InformationItem]:
        """
        Collect Instagram posts about Nairobi.

        Args:
            query: Search query or hashtag
            limit: Maximum number of posts to collect

        Returns:
            List of InformationItem objects
        """
        if not self.client:
            self.logger.warning("Instagram client not initialized. Skipping collection.")
            return []

        self.logger.info(f"Collecting Instagram posts for: {query}")

        items = []

        try:
            # Search for hashtag
            hashtag = query.replace('#', '').lower()

            # Get top posts for hashtag
            posts = self.client.hashtag_medias_top(hashtag, amount=min(limit, 50))

            for post in posts:
                try:
                    # Extract post data
                    caption = post.caption_text if hasattr(post, 'caption_text') else ""
                    username = post.user.username if hasattr(post, 'user') else "unknown"

                    # Create title
                    title = f"@{username}: {caption[:50]}..." if len(caption) > 50 else f"@{username}: {caption}"

                    # Extract hashtags
                    hashtags = self.text_processor.extract_hashtags(caption)

                    # Extract location if available
                    location = None
                    if hasattr(post, 'location') and post.location:
                        location = post.location.name

                    # Get engagement metrics
                    likes = post.like_count if hasattr(post, 'like_count') else 0
                    comments = post.comment_count if hasattr(post, 'comment_count') else 0

                    # Determine category
                    category = self._categorize_post(caption, hashtags)

                    item = self.create_information_item(
                        title=title,
                        summary=caption or "Instagram post",
                        category=category,
                        source_url=f"https://www.instagram.com/p/{post.code}/" if hasattr(post, 'code') else None,
                        timestamp=post.taken_at if hasattr(post, 'taken_at') else datetime.utcnow(),
                        location=location,
                        tags=hashtags,
                        metadata={
                            'platform': 'instagram',
                            'author': username,
                            'likes': likes,
                            'comments': comments,
                            'engagement': likes + comments,
                            'media_type': post.media_type if hasattr(post, 'media_type') else 'unknown'
                        }
                    )

                    items.append(item)

                except Exception as e:
                    self.logger.warning(f"Error processing Instagram post: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error collecting Instagram posts: {e}")

        # Filter and deduplicate
        items = self.filter_relevant_items(items)
        items = self.deduplicate_items(items)

        self.logger.info(f"Collected {len(items)} relevant Instagram posts")
        return items

    def collect_location_posts(self, location_id: int, limit: int = 30) -> List[InformationItem]:
        """
        Collect posts from a specific location.

        Args:
            location_id: Instagram location ID
            limit: Maximum number of posts

        Returns:
            List of InformationItem objects
        """
        if not self.client:
            return []

        try:
            posts = self.client.location_medias_top(location_id, amount=min(limit, 50))

            items = []
            for post in posts:
                try:
                    caption = post.caption_text if hasattr(post, 'caption_text') else ""
                    username = post.user.username if hasattr(post, 'user') else "unknown"

                    title = f"@{username} at location"

                    item = self.create_information_item(
                        title=title,
                        summary=caption or "Instagram post from location",
                        category=Category.SOCIAL_MEDIA,
                        source_url=f"https://www.instagram.com/p/{post.code}/" if hasattr(post, 'code') else None,
                        timestamp=post.taken_at if hasattr(post, 'taken_at') else datetime.utcnow(),
                        metadata={
                            'platform': 'instagram',
                            'author': username,
                            'location_id': location_id
                        }
                    )

                    items.append(item)

                except Exception as e:
                    continue

            return self.filter_relevant_items(items)

        except Exception as e:
            self.logger.error(f"Error collecting location posts: {e}")
            return []

    def _categorize_post(self, caption: str, hashtags: List[str]) -> Category:
        """Categorize Instagram post."""
        text_lower = f"{caption} {' '.join(hashtags)}".lower()

        # Check for food/nightlife
        if any(word in text_lower for word in ['food', 'foodie', 'restaurant', 'dining', 'brunch']):
            return Category.FOOD_NIGHTLIFE

        # Check for events/culture
        if any(word in text_lower for word in ['event', 'concert', 'art', 'exhibition', 'festival']):
            return Category.CULTURE_EVENTS

        # Check for tourism
        if any(word in text_lower for word in ['travel', 'tourism', 'visit', 'explore', 'adventure']):
            return Category.TOURISM

        return Category.SOCIAL_MEDIA
