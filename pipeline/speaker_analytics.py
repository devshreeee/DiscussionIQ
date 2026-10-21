# pipeline/speaker_analytics.py
import pandas as pd
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DiscussionAnalyticsEngine:
    def __init__(self, transcript_segments: List[Dict[str, Any]], classifications: List[Dict[str, Any]]):
        """
        Initializes the analytics engine with transcript and classification data.
        """
        self.segments_df = pd.DataFrame(transcript_segments)
        self.classifications_df = pd.DataFrame(classifications)
        
        # Merge segments with their classifications if data is present
        if not self.segments_df.empty and not self.classifications_df.empty:
            self.merged_df = pd.merge(
                self.segments_df, 
                self.classifications_df, 
                left_on='id', 
                right_on='segment_id', 
                how='left'
            )
        else:
            self.merged_df = pd.DataFrame()

    def get_participant_contributions(self) -> Dict[str, Dict[str, Any]]:
        """
        Calculates speaking time and turn frequency for each participant.
        """
        if self.segments_df.empty:
            return {}

        self.segments_df['duration'] = self.segments_df['end_time'] - self.segments_df['start_time']
        
        stats = {}
        grouped = self.segments_df.groupby('speaker_label')
        
        for speaker, group in grouped:
            stats[speaker] = {
                "total_speaking_time_seconds": group['duration'].sum(),
                "turn_count": len(group),
                "average_turn_duration": group['duration'].mean()
            }
        return stats

    def get_category_distribution(self) -> Dict[str, int]:
        """
        Returns the frequency of each verified communication category.
        """
        if self.merged_df.empty or 'category_name' not in self.merged_df.columns:
            return {}
            
        distribution = self.merged_df['category_name'].value_counts().to_dict()
        return distribution

    def track_sentiment_trajectory(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Tracks the temporal evolution of sentiment per speaker.
        """
        if self.merged_df.empty or 'sentiment' not in self.merged_df.columns:
            return {}

        trajectory = {}
        # Sort chronologically
        sorted_df = self.merged_df.sort_values(by='start_time')
        
        grouped = sorted_df.groupby('speaker_label')
        for speaker, group in grouped:
            # Map sentiments to numeric values for trend analysis if needed, 
            # but returning raw timeline for now.
            trajectory[speaker] = group[['start_time', 'sentiment', 'category_name']].to_dict('records')
            
        return trajectory

    def extract_action_items(self) -> List[Dict[str, Any]]:
        """
        Extracts segments classified as 'Decision Making' or 'Strategising' 
        that contain actionable evidence.
        """
        if self.merged_df.empty or 'category_name' not in self.merged_df.columns:
            return []

        action_categories = ['Decision Making', 'Strategising']
        action_df = self.merged_df[self.merged_df['category_name'].isin(action_categories)]
        
        # Filter for rows that actually have an evidence span extracted by the LLM
        action_df = action_df.dropna(subset=['evidence_span'])
        
        return action_df[['speaker_label', 'start_time', 'category_name', 'evidence_span']].to_dict('records')
