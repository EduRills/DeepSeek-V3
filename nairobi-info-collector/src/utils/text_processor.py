"""Text processing utilities for content analysis."""

import re
from typing import List, Optional
from datetime import datetime
from langdetect import detect, LangDetectException
from textblob import TextBlob


class TextProcessor:
    """Utilities for processing and analyzing text content."""

    NAIROBI_KEYWORDS = [
        'nairobi', 'nbo', 'nairobia', 'kenya', 'kenyan',
        'westlands', 'kilimani', 'karen', 'lavington', 'kileleshwa',
        'ngong', 'kasarani', 'embakasi', 'kibera', 'kangemi',
        'upperhill', 'cbd', 'uhuru park', 'karura', 'kcb', 'safaricom'
    ]

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\-\'"()]', '', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    @staticmethod
    def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text.

        Args:
            text: Input text
            min_length: Minimum keyword length
            max_keywords: Maximum number of keywords to return

        Returns:
            List of keywords
        """
        if not text:
            return []

        # Convert to lowercase and split
        words = text.lower().split()

        # Filter words
        keywords = [
            word for word in words
            if len(word) >= min_length
            and word.isalpha()
            and word not in {'the', 'and', 'for', 'that', 'this', 'with', 'from'}
        ]

        # Get unique keywords (preserve order)
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)

        return unique_keywords[:max_keywords]

    @staticmethod
    def calculate_relevance_score(text: str, keywords: Optional[List[str]] = None) -> float:
        """
        Calculate relevance score based on Nairobi-related keywords.

        Args:
            text: Text to analyze
            keywords: Additional keywords to check (optional)

        Returns:
            Relevance score between 0 and 1
        """
        if not text:
            return 0.0

        text_lower = text.lower()

        # Check for Nairobi-specific keywords
        all_keywords = TextProcessor.NAIROBI_KEYWORDS.copy()
        if keywords:
            all_keywords.extend([k.lower() for k in keywords])

        matches = sum(1 for keyword in all_keywords if keyword in text_lower)
        total_keywords = len(all_keywords)

        # Calculate score (cap at 1.0)
        score = min(matches / 10.0, 1.0)  # Normalize by 10 keywords

        return round(score, 2)

    @staticmethod
    def detect_language(text: str) -> Optional[str]:
        """
        Detect the language of the text.

        Args:
            text: Input text

        Returns:
            Language code (e.g., 'en', 'sw') or None
        """
        if not text or len(text) < 10:
            return None

        try:
            return detect(text)
        except LangDetectException:
            return None

    @staticmethod
    def analyze_sentiment(text: str) -> str:
        """
        Analyze sentiment of the text.

        Args:
            text: Input text

        Returns:
            Sentiment: 'positive', 'negative', or 'neutral'
        """
        if not text:
            return "neutral"

        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity

            if polarity > 0.1:
                return "positive"
            elif polarity < -0.1:
                return "negative"
            else:
                return "neutral"
        except Exception:
            return "neutral"

    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """
        Extract hashtags from text.

        Args:
            text: Input text

        Returns:
            List of hashtags
        """
        if not text:
            return []

        hashtags = re.findall(r'#(\w+)', text)
        return list(set(hashtags))  # Remove duplicates

    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """
        Extract @mentions from text.

        Args:
            text: Input text

        Returns:
            List of mentions
        """
        if not text:
            return []

        mentions = re.findall(r'@(\w+)', text)
        return list(set(mentions))  # Remove duplicates

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """
        Extract URLs from text.

        Args:
            text: Input text

        Returns:
            List of URLs
        """
        if not text:
            return []

        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return urls

    @staticmethod
    def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
        """
        Truncate text to specified length.

        Args:
            text: Input text
            max_length: Maximum length
            suffix: Suffix to add if truncated

        Returns:
            Truncated text
        """
        if not text or len(text) <= max_length:
            return text

        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def is_nairobi_related(text: str, threshold: float = 0.3) -> bool:
        """
        Check if text is related to Nairobi.

        Args:
            text: Input text
            threshold: Minimum relevance score threshold

        Returns:
            True if related to Nairobi
        """
        score = TextProcessor.calculate_relevance_score(text)
        return score >= threshold
