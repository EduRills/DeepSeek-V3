"""YouTube data collector using YouTube Data API."""

from typing import List, Optional
from datetime import datetime, timedelta
import os

from .base_collector import BaseCollector
from src.models import InformationItem, ReliabilityLevel, Category


class YouTubeCollector(BaseCollector):
    """
    Collector for YouTube videos and content.

    Note: Requires YouTube Data API key.
    """

    def __init__(self):
        """Initialize YouTube collector."""
        super().__init__("YouTube", ReliabilityLevel.MEDIUM)

        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.service = None

        if self.api_key:
            self._init_client()

    def _init_client(self):
        """Initialize YouTube API client."""
        try:
            from googleapiclient.discovery import build

            self.service = build('youtube', 'v3', developerKey=self.api_key)
            self.logger.info("YouTube API client initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize YouTube client: {e}")
            self.service = None

    def collect(self, query: str = "Nairobi Kenya", limit: int = 50) -> List[InformationItem]:
        """
        Collect YouTube videos about Nairobi.

        Args:
            query: Search query
            limit: Maximum number of videos to collect

        Returns:
            List of InformationItem objects
        """
        if not self.service:
            self.logger.warning("YouTube service not initialized. Skipping collection.")
            return []

        self.logger.info(f"Collecting YouTube videos for: {query}")

        items = []

        try:
            # Calculate date for recent videos (last 30 days)
            published_after = (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z'

            # Search for videos
            search_response = self.service.search().list(
                q=query,
                part='id,snippet',
                maxResults=min(limit, 50),
                order='relevance',
                type='video',
                publishedAfter=published_after,
                relevanceLanguage='en'
            ).execute()

            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]

            if not video_ids:
                self.logger.info("No videos found")
                return []

            # Get detailed statistics for videos
            videos_response = self.service.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()

            for video in videos_response.get('items', []):
                try:
                    snippet = video['snippet']
                    statistics = video.get('statistics', {})

                    # Extract data
                    title = snippet['title']
                    description = snippet['description']
                    channel_title = snippet['channelTitle']
                    published_at = snippet['publishedAt']

                    # Extract metrics
                    views = int(statistics.get('viewCount', 0))
                    likes = int(statistics.get('likeCount', 0))
                    comments = int(statistics.get('commentCount', 0))

                    # Extract tags
                    tags = snippet.get('tags', [])

                    # Create summary
                    summary = self.text_processor.truncate_text(description, max_length=200)

                    # Determine category
                    category = self._categorize_video(title, description, tags)

                    # Create URL
                    video_url = f"https://www.youtube.com/watch?v={video['id']}"

                    item = self.create_information_item(
                        title=title,
                        summary=summary,
                        content=description,
                        category=category,
                        source_url=video_url,
                        timestamp=datetime.fromisoformat(published_at.replace('Z', '+00:00')),
                        tags=tags[:10],  # Limit tags
                        metadata={
                            'platform': 'youtube',
                            'channel': channel_title,
                            'views': views,
                            'likes': likes,
                            'comments': comments,
                            'engagement': likes + comments,
                            'video_id': video['id']
                        }
                    )

                    items.append(item)

                except Exception as e:
                    self.logger.warning(f"Error processing video: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error collecting YouTube videos: {e}")

        # Filter and deduplicate
        items = self.filter_relevant_items(items)
        items = self.deduplicate_items(items)

        self.logger.info(f"Collected {len(items)} relevant YouTube videos")
        return items

    def _categorize_video(self, title: str, description: str, tags: List[str]) -> Category:
        """Categorize YouTube video."""
        text_lower = f"{title} {description} {' '.join(tags)}".lower()

        # Check for tourism/travel
        if any(word in text_lower for word in ['travel', 'tour', 'visit', 'vlog', 'explore']):
            return Category.TOURISM

        # Check for events
        if any(word in text_lower for word in ['concert', 'festival', 'event', 'live']):
            return Category.CULTURE_EVENTS

        # Check for food
        if any(word in text_lower for word in ['food', 'restaurant', 'cuisine', 'dining']):
            return Category.FOOD_NIGHTLIFE

        # Check for business/tech
        if any(word in text_lower for word in ['business', 'startup', 'tech', 'innovation', 'entrepreneur']):
            return Category.BUSINESS_ECONOMY

        return Category.SOCIAL_MEDIA
