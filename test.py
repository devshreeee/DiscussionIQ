from database.dashboard_queries import (
    get_dashboard_stats,
    get_recent_meetings,
    get_meeting,
    get_transcript,
    get_analysis,
    get_speaker_segments,
    get_speaker_analytics,
    get_themes,
    get_key_points,
    get_decisions,
    get_action_items,
    get_unresolved_issues
)


def main():

    print()
    print("=" * 60)
    print("Testing DiscussionIQ Dashboard Queries")
    print("=" * 60)
    print()

    # ========================================================
    # DASHBOARD STATS
    # ========================================================

    stats = get_dashboard_stats()

    print("Dashboard Statistics:")
    print(stats)

    print()

    # ========================================================
    # RECENT MEETINGS
    # ========================================================

    meetings = get_recent_meetings(
        limit=5
    )

    print(
        f"Recent meetings: {len(meetings)}"
    )

    for meeting in meetings:

        print(
            f"  #{meeting['id']} "
            f"{meeting['filename']} "
            f"({meeting['status']})"
        )

    print()

    # ========================================================
    # STOP IF NO MEETINGS
    # ========================================================

    if not meetings:

        print(
            "No meetings found."
        )

        return

    # ========================================================
    # USE MOST RECENT MEETING
    # ========================================================

    meeting_id = meetings[0]["id"]

    print(
        f"Testing meeting ID: {meeting_id}"
    )

    print()

    # ========================================================
    # MEETING
    # ========================================================

    meeting = get_meeting(
        meeting_id
    )

    print("Meeting:")
    print(meeting)

    print()

    # ========================================================
    # TRANSCRIPT
    # ========================================================

    transcript = get_transcript(
        meeting_id
    )

    if transcript is None:

        print(
            "❌ Transcript not found."
        )

        return

    transcript_id = transcript["id"]

    print(
        f"Transcript ID: {transcript_id}"
    )

    print(
        f"Transcript characters: "
        f"{len(transcript['transcript_text'])}"
    )

    print()

    # ========================================================
    # ANALYSIS
    # ========================================================

    analysis = get_analysis(
        transcript_id
    )

    if analysis is None:

        print(
            "❌ Analysis not found."
        )

        return

    analysis_id = analysis["id"]

    print(
        f"Analysis ID: {analysis_id}"
    )

    print(
        f"Sentiment: "
        f"{analysis['sentiment']}"
    )

    print(
        f"Sentiment score: "
        f"{analysis['sentiment_score']}"
    )

    print()

    # ========================================================
    # SPEAKER SEGMENTS
    # ========================================================

    segments = get_speaker_segments(
        transcript_id
    )

    print(
        f"Speaker segments: "
        f"{len(segments)}"
    )

    if segments:

        print(
            "First segment:"
        )

        print(
            segments[0]
        )

    print()

    # ========================================================
    # SPEAKER ANALYTICS
    # ========================================================

    speaker_stats = (
        get_speaker_analytics(
            transcript_id
        )
    )

    print(
        f"Speaker analytics: "
        f"{len(speaker_stats)}"
    )

    for speaker in speaker_stats:

        print(
            f"  {speaker['speaker']}: "
            f"{speaker['participation_percentage']}%"
        )

    print()

    # ========================================================
    # THEMES
    # ========================================================

    themes = get_themes(
        analysis_id
    )

    print(
        f"Themes: {len(themes)}"
    )

    for theme in themes:

        print(
            f"  • {theme['theme']}"
        )

    print()

    # ========================================================
    # KEY POINTS
    # ========================================================

    key_points = get_key_points(
        analysis_id
    )

    print(
        f"Key points: "
        f"{len(key_points)}"
    )

    print()

    # ========================================================
    # DECISIONS
    # ========================================================

    decisions = get_decisions(
        analysis_id
    )

    print(
        f"Decisions: "
        f"{len(decisions)}"
    )

    print()

    # ========================================================
    # ACTION ITEMS
    # ========================================================

    action_items = get_action_items(
        analysis_id
    )

    print(
        f"Action items: "
        f"{len(action_items)}"
    )

    print()

    # ========================================================
    # UNRESOLVED ISSUES
    # ========================================================

    unresolved = (
        get_unresolved_issues(
            analysis_id
        )
    )

    print(
        f"Unresolved issues: "
        f"{len(unresolved)}"
    )

    print()

    # ========================================================
    # FINAL
    # ========================================================

    print("=" * 60)
    print(
        "✅ DASHBOARD QUERY TEST PASSED"
    )
    print("=" * 60)
    print()


if __name__ == "__main__":

    main()