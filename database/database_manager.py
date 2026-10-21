from database.db_connection import get_connection


# ============================================================
# MEETINGS
# ============================================================

def create_meeting(
    filename,
    duration_seconds=None,
    status="processing"
):
    """
    Create a new meeting record.

    Returns:
        int: Meeting ID
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO meetings
                (
                    filename,
                    duration_seconds,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
                RETURNING id
                """,
                (
                    filename,
                    duration_seconds,
                    status
                )
            )

            result = cur.fetchone()

            if result is None:
                raise RuntimeError(
                    "Failed to create meeting."
                )

            meeting_id = result[0]

        conn.commit()

        return meeting_id

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def update_meeting_status(
    meeting_id,
    status
):
    """
    Update the processing status of a meeting.

    Examples:
        processing
        completed
        failed
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                UPDATE meetings
                SET status = %s
                WHERE id = %s
                """,
                (
                    status,
                    meeting_id
                )
            )

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


# ============================================================
# TRANSCRIPTS
# ============================================================

def save_transcript(
    filename,
    transcript_text,
    meeting_id=None
):
    """
    Save a transcript.

    Returns:
        int: Transcript ID
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO transcripts
                (
                    meeting_id,
                    filename,
                    transcript_text
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
                RETURNING id
                """,
                (
                    meeting_id,
                    filename,
                    transcript_text
                )
            )

            result = cur.fetchone()

            if result is None:
                raise RuntimeError(
                    "Failed to create transcript."
                )

            transcript_id = result[0]

        conn.commit()

        return transcript_id

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def get_transcript(
    transcript_id
):
    """
    Retrieve a single transcript.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    meeting_id,
                    filename,
                    transcript_text,
                    created_at
                FROM transcripts
                WHERE id = %s
                """,
                (transcript_id,)
            )

            row = cur.fetchone()

            if row is None:
                return None

            return {
                "id": row[0],
                "meeting_id": row[1],
                "filename": row[2],
                "transcript_text": row[3],
                "created_at": row[4]
            }

    finally:

        conn.close()


def get_all_transcripts():
    """
    Retrieve all transcripts, newest first.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    meeting_id,
                    filename,
                    transcript_text,
                    created_at
                FROM transcripts
                ORDER BY created_at DESC
                """
            )

            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "meeting_id": row[1],
                    "filename": row[2],
                    "transcript_text": row[3],
                    "created_at": row[4]
                }
                for row in rows
            ]

    finally:

        conn.close()


# ============================================================
# SPEAKER SEGMENTS
# ============================================================

def save_speaker_segment(
    transcript_id,
    speaker,
    start_time,
    end_time,
    text=None
):
    """
    Save one speaker segment.

    Returns:
        int: Segment ID
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO speaker_segments
                (
                    transcript_id,
                    speaker,
                    start_time,
                    end_time,
                    text
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING id
                """,
                (
                    transcript_id,
                    speaker,
                    start_time,
                    end_time,
                    text
                )
            )

            result = cur.fetchone()

            if result is None:
                raise RuntimeError(
                    "Failed to save speaker segment."
                )

            segment_id = result[0]

        conn.commit()

        return segment_id

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def save_speaker_segments(
    transcript_id,
    segments
):
    """
    Save multiple speaker segments.

    Expected format:

    [
        {
            "speaker": "SPEAKER_00",
            "start": 0.0,
            "end": 5.4,
            "text": "Hello everyone."
        }
    ]
    """

    if not segments:
        return

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            for segment in segments:

                cur.execute(
                    """
                    INSERT INTO speaker_segments
                    (
                        transcript_id,
                        speaker,
                        start_time,
                        end_time,
                        text
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        transcript_id,
                        segment["speaker"],
                        segment["start"],
                        segment["end"],
                        segment.get("text")
                    )
                )

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def get_speaker_segments(
    transcript_id
):
    """
    Retrieve speaker segments in chronological order.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    transcript_id,
                    speaker,
                    start_time,
                    end_time,
                    text
                FROM speaker_segments
                WHERE transcript_id = %s
                ORDER BY start_time ASC
                """,
                (transcript_id,)
            )

            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "transcript_id": row[1],
                    "speaker": row[2],
                    "start_time": row[3],
                    "end_time": row[4],
                    "text": row[5]
                }
                for row in rows
            ]

    finally:

        conn.close()


# ============================================================
# ANALYSIS
# ============================================================

def save_analysis(
    transcript_id,
    themes,
    sentiment,
    summary,
    full_analysis,
    sentiment_score=None
):
    """
    Save AI analysis for a transcript.

    full_analysis may be either:
        - a Python dictionary
        - a JSON string
        - regular text

    The database stores full_analysis as TEXT.
    """

    import json

    conn = get_connection()
    cur = conn.cursor()

    # --------------------------------------------------------
    # Convert structured analysis dictionary to JSON text
    # --------------------------------------------------------

    if isinstance(
        full_analysis,
        dict
    ):

        full_analysis_text = json.dumps(
            full_analysis,
            ensure_ascii=False,
            indent=2
        )

    elif isinstance(
        full_analysis,
        str
    ):

        full_analysis_text = (
            full_analysis
        )

    else:

        full_analysis_text = str(
            full_analysis
        )

    # --------------------------------------------------------
    # Convert themes to text if necessary
    # --------------------------------------------------------

    if isinstance(
        themes,
        list
    ):

        themes_text = "\n".join(
            str(theme)
            for theme in themes
        )

    else:

        themes_text = str(
            themes
        )

    # --------------------------------------------------------
    # Insert analysis
    # --------------------------------------------------------

    cur.execute(
        """
        INSERT INTO analyses
        (
            transcript_id,
            themes,
            sentiment,
            summary,
            full_analysis,
            sentiment_score
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id
        """,
        (
            transcript_id,
            themes_text,
            sentiment,
            summary,
            full_analysis_text,
            sentiment_score
        )
    )

    row = cur.fetchone()

    if row is None:

        conn.rollback()

        cur.close()
        conn.close()

        raise RuntimeError(
            "Failed to retrieve analysis ID "
            "after insert."
        )

    analysis_id = row[0]

    conn.commit()

    cur.close()
    conn.close()

    return analysis_id

def get_analysis(
    transcript_id
):
    """
    Retrieve the latest analysis for a transcript.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    transcript_id,
                    themes,
                    sentiment,
                    sentiment_score,
                    summary,
                    full_analysis,
                    created_at
                FROM analyses
                WHERE transcript_id = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (transcript_id,)
            )

            row = cur.fetchone()

            if row is None:
                return None

            return {
                "id": row[0],
                "transcript_id": row[1],
                "themes": row[2],
                "sentiment": row[3],
                "sentiment_score": row[4],
                "summary": row[5],
                "full_analysis": row[6],
                "created_at": row[7]
            }

    finally:

        conn.close()


# ============================================================
# THEMES
# ============================================================

def save_themes(
    analysis_id,
    themes
):
    """
    Save extracted discussion themes.

    Example:
        ["Budget", "Planning", "Technology"]
    """

    if not themes:
        return

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            for theme in themes:

                cur.execute(
                    """
                    INSERT INTO themes
                    (
                        analysis_id,
                        theme
                    )
                    VALUES
                    (
                        %s,
                        %s
                    )
                    """,
                    (
                        analysis_id,
                        theme
                    )
                )

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def get_themes(
    analysis_id
):
    """
    Retrieve themes for an analysis.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    theme
                FROM themes
                WHERE analysis_id = %s
                ORDER BY id ASC
                """,
                (analysis_id,)
            )

            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "theme": row[1]
                }
                for row in rows
            ]

    finally:

        conn.close()


# ============================================================
# KEY POINTS
# ============================================================

def save_key_points(
    analysis_id,
    points
):
    """
    Save key discussion points.
    """

    if not points:
        return

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            for point in points:

                cur.execute(
                    """
                    INSERT INTO key_points
                    (
                        analysis_id,
                        point
                    )
                    VALUES
                    (
                        %s,
                        %s
                    )
                    """,
                    (
                        analysis_id,
                        point
                    )
                )

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def get_key_points(
    analysis_id
):
    """
    Retrieve key discussion points.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    point
                FROM key_points
                WHERE analysis_id = %s
                ORDER BY id ASC
                """,
                (analysis_id,)
            )

            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "point": row[1]
                }
                for row in rows
            ]

    finally:

        conn.close()


# ============================================================
# DECISIONS
# ============================================================

def save_decisions(
    analysis_id,
    decisions
):
    """
    Save discussion decisions.

    Expected format:

    [
        {
            "decision": "Use PostgreSQL",
            "speaker": "SPEAKER_01"
        }
    ]
    """

    if not decisions:
        return

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            for item in decisions:

                if isinstance(item, dict):

                    decision = item.get(
                        "decision",
                        ""
                    )

                    speaker = item.get(
                        "speaker"
                    )

                else:

                    decision = str(item)

                    speaker = None

                if not decision:
                    continue

                cur.execute(
                    """
                    INSERT INTO decisions
                    (
                        analysis_id,
                        decision,
                        speaker
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        analysis_id,
                        decision,
                        speaker
                    )
                )

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def get_decisions(
    analysis_id
):
    """
    Retrieve decisions.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    decision,
                    speaker
                FROM decisions
                WHERE analysis_id = %s
                ORDER BY id ASC
                """,
                (analysis_id,)
            )

            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "decision": row[1],
                    "speaker": row[2]
                }
                for row in rows
            ]

    finally:

        conn.close()


# ============================================================
# ACTION ITEMS
# ============================================================

def save_action_items(
    analysis_id,
    action_items
):
    """
    Save action items.

    Expected format:

    [
        {
            "task": "Complete testing",
            "speaker": "SPEAKER_02",
            "priority": "High"
        }
    ]
    """

    if not action_items:
        return

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            for item in action_items:

                if isinstance(item, dict):

                    task = item.get(
                        "task",
                        ""
                    )

                    speaker = item.get(
                        "speaker"
                    )

                    priority = item.get(
                        "priority"
                    )

                else:

                    task = str(item)

                    speaker = None

                    priority = None

                if not task:
                    continue

                cur.execute(
                    """
                    INSERT INTO action_items
                    (
                        analysis_id,
                        task,
                        speaker,
                        priority
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        analysis_id,
                        task,
                        speaker,
                        priority
                    )
                )

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def get_action_items(
    analysis_id
):
    """
    Retrieve action items.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    task,
                    speaker,
                    priority,
                    status
                FROM action_items
                WHERE analysis_id = %s
                ORDER BY id ASC
                """,
                (analysis_id,)
            )

            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "task": row[1],
                    "speaker": row[2],
                    "priority": row[3],
                    "status": row[4]
                }
                for row in rows
            ]

    finally:

        conn.close()


# ============================================================
# UNRESOLVED ISSUES
# ============================================================

def save_unresolved_issues(
    analysis_id,
    issues
):
    """
    Save unresolved discussion issues.
    """

    if not issues:
        return

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            for issue in issues:

                cur.execute(
                    """
                    INSERT INTO unresolved_issues
                    (
                        analysis_id,
                        issue
                    )
                    VALUES
                    (
                        %s,
                        %s
                    )
                    """,
                    (
                        analysis_id,
                        issue
                    )
                )

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def get_unresolved_issues(
    analysis_id
):
    """
    Retrieve unresolved issues.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    issue
                FROM unresolved_issues
                WHERE analysis_id = %s
                ORDER BY id ASC
                """,
                (analysis_id,)
            )

            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "issue": row[1]
                }
                for row in rows
            ]

    finally:

        conn.close()


# ============================================================
# SPEAKER ANALYTICS
# ============================================================

def save_speaker_analytics(
    transcript_id,
    analytics
):
    """
    Save calculated speaker participation metrics.

    Expected format:

    [
        {
            "speaker": "SPEAKER_00",
            "speaking_time_seconds": 120.5,
            "segment_count": 10,
            "word_count": 245,
            "participation_percentage": 52.4
        }
    ]
    """

    if not analytics:
        return

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            for item in analytics:

                cur.execute(
                    """
                    INSERT INTO speaker_analytics
                    (
                        transcript_id,
                        speaker,
                        speaking_time_seconds,
                        segment_count,
                        word_count,
                        participation_percentage
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        transcript_id,
                        item["speaker"],
                        item.get(
                            "speaking_time_seconds"
                        ),
                        item.get(
                            "segment_count"
                        ),
                        item.get(
                            "word_count"
                        ),
                        item.get(
                            "participation_percentage"
                        )
                    )
                )

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def get_speaker_analytics(
    transcript_id
):
    """
    Retrieve speaker analytics.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    speaker,
                    speaking_time_seconds,
                    segment_count,
                    word_count,
                    participation_percentage
                FROM speaker_analytics
                WHERE transcript_id = %s
                ORDER BY speaking_time_seconds DESC
                """,
                (transcript_id,)
            )

            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "speaker": row[1],
                    "speaking_time_seconds": row[2],
                    "segment_count": row[3],
                    "word_count": row[4],
                    "participation_percentage": row[5]
                }
                for row in rows
            ]

    finally:

        conn.close()


# ============================================================
# MODEL EVALUATION
# ============================================================

def save_model_evaluation(
    transcript_id,
    wer,
    accuracy_percentage,
    evaluation_type="transcription"
):
    """
    Save model evaluation results.

    Returns:
        int: Evaluation ID
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO model_evaluations
                (
                    transcript_id,
                    wer,
                    accuracy_percentage,
                    evaluation_type
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING id
                """,
                (
                    transcript_id,
                    wer,
                    accuracy_percentage,
                    evaluation_type
                )
            )

            result = cur.fetchone()

            if result is None:
                raise RuntimeError(
                    "Failed to save model evaluation."
                )

            evaluation_id = result[0]

        conn.commit()

        return evaluation_id

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def get_model_evaluation(
    transcript_id
):
    """
    Retrieve the latest evaluation for a transcript.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    transcript_id,
                    wer,
                    accuracy_percentage,
                    evaluation_type,
                    created_at
                FROM model_evaluations
                WHERE transcript_id = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (transcript_id,)
            )

            row = cur.fetchone()

            if row is None:
                return None

            return {
                "id": row[0],
                "transcript_id": row[1],
                "wer": row[2],
                "accuracy_percentage": row[3],
                "evaluation_type": row[4],
                "created_at": row[5]
            }

    finally:

        conn.close()


# ============================================================
# COMPLETE MEETING DATA
# ============================================================

def get_meeting_details(
    meeting_id
):
    """
    Retrieve a complete meeting overview.

    This function is intended for the dashboard.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            # ------------------------------------------------
            # Meeting
            # ------------------------------------------------

            cur.execute(
                """
                SELECT
                    id,
                    filename,
                    duration_seconds,
                    status,
                    created_at
                FROM meetings
                WHERE id = %s
                """,
                (meeting_id,)
            )

            meeting_row = cur.fetchone()

            if meeting_row is None:
                return None

            meeting = {
                "id": meeting_row[0],
                "filename": meeting_row[1],
                "duration_seconds": meeting_row[2],
                "status": meeting_row[3],
                "created_at": meeting_row[4]
            }

            # ------------------------------------------------
            # Transcript
            # ------------------------------------------------

            cur.execute(
                """
                SELECT
                    id,
                    filename,
                    transcript_text,
                    created_at
                FROM transcripts
                WHERE meeting_id = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (meeting_id,)
            )

            transcript_row = cur.fetchone()

            if transcript_row:

                transcript = {
                    "id": transcript_row[0],
                    "filename": transcript_row[1],
                    "transcript_text": transcript_row[2],
                    "created_at": transcript_row[3]
                }

                meeting["transcript"] = transcript

                transcript_id = transcript_row[0]

            else:

                meeting["transcript"] = None

                transcript_id = None

            # ------------------------------------------------
            # Analysis
            # ------------------------------------------------

            if transcript_id:

                cur.execute(
                    """
                    SELECT
                        id,
                        themes,
                        sentiment,
                        sentiment_score,
                        summary,
                        full_analysis,
                        created_at
                    FROM analyses
                    WHERE transcript_id = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (transcript_id,)
                )

                analysis_row = cur.fetchone()

                if analysis_row:

                    meeting["analysis"] = {
                        "id": analysis_row[0],
                        "themes": analysis_row[1],
                        "sentiment": analysis_row[2],
                        "sentiment_score": analysis_row[3],
                        "summary": analysis_row[4],
                        "full_analysis": analysis_row[5],
                        "created_at": analysis_row[6]
                    }

                else:

                    meeting["analysis"] = None

            else:

                meeting["analysis"] = None

            return meeting

    finally:

        conn.close()


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

def get_dashboard_statistics():
    """
    Retrieve high-level statistics for the dashboard.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            # Total meetings

            cur.execute(
                """
                SELECT COUNT(*)
                FROM meetings
                """
            )

            total_meetings = cur.fetchone()[0] # type: ignore

            # Completed meetings

            cur.execute(
                """
                SELECT COUNT(*)
                FROM meetings
                WHERE status = 'completed'
                """
            )

            completed_meetings = cur.fetchone()[0] # type: ignore

            # Total transcripts

            cur.execute(
                """
                SELECT COUNT(*)
                FROM transcripts
                """
            )

            total_transcripts = cur.fetchone()[0] # type: ignore

            # Total speakers

            cur.execute(
                """
                SELECT COUNT(
                    DISTINCT speaker
                )
                FROM speaker_segments
                """
            )

            total_speakers = cur.fetchone()[0] # type: ignore

            # Total analyses

            cur.execute(
                """
                SELECT COUNT(*)
                FROM analyses
                """
            )

            total_analyses = cur.fetchone()[0] # type: ignore

            # Average sentiment

            cur.execute(
                """
                SELECT AVG(sentiment_score)
                FROM analyses
                WHERE sentiment_score IS NOT NULL
                """
            )

            average_sentiment = cur.fetchone()[0] # type: ignore

            return {
                "total_meetings": total_meetings,
                "completed_meetings": completed_meetings,
                "total_transcripts": total_transcripts,
                "total_speakers": total_speakers,
                "total_analyses": total_analyses,
                "average_sentiment": average_sentiment
            }

    finally:

        conn.close()


# ============================================================
# DELETE MEETING
# ============================================================

def delete_meeting(
    meeting_id
):
    """
    Delete a meeting.

    Related transcripts and dependent records are removed
    through ON DELETE CASCADE relationships.
    """

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            cur.execute(
                """
                DELETE FROM meetings
                WHERE id = %s
                """,
                (meeting_id,)
            )

            deleted = cur.rowcount

        conn.commit()

        return deleted > 0

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()