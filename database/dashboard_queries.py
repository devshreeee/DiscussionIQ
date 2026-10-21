from database.db_connection import get_connection


# ============================================================
# DASHBOARD OVERVIEW
# ============================================================

def get_dashboard_stats():
    """
    Get high-level statistics for the dashboard.
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT
                COUNT(*) AS total_meetings,

                COUNT(*) FILTER (
                    WHERE status = 'completed'
                ) AS completed_meetings,

                COUNT(*) FILTER (
                    WHERE status = 'failed'
                ) AS failed_meetings,

                COALESCE(
                    SUM(duration_seconds),
                    0
                ) AS total_duration

            FROM meetings
            """
        )

        row = cur.fetchone()

        if row is None:

            return {
                "total_meetings": 0,
                "completed_meetings": 0,
                "failed_meetings": 0,
                "total_duration": 0
            }

        return {
            "total_meetings": row[0],
            "completed_meetings": row[1],
            "failed_meetings": row[2],
            "total_duration": float(
                row[3]
            )
        }

    finally:

        cur.close()
        conn.close()


# ============================================================
# RECENT MEETINGS
# ============================================================

def get_recent_meetings(
    limit=10
):
    """
    Get recent meetings for dashboard display.
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT
                id,
                filename,
                duration_seconds,
                status,
                created_at

            FROM meetings

            ORDER BY created_at DESC

            LIMIT %s
            """,
            (limit,)
        )

        rows = cur.fetchall()

        meetings = []

        for row in rows:

            meetings.append(
                {
                    "id": row[0],
                    "filename": row[1],
                    "duration_seconds": (
                        float(row[2])
                        if row[2] is not None
                        else 0.0
                    ),
                    "status": row[3],
                    "created_at": row[4]
                }
            )

        return meetings

    finally:

        cur.close()
        conn.close()


# ============================================================
# SINGLE MEETING
# ============================================================

def get_meeting(
    meeting_id
):
    """
    Get a single meeting.
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

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

        row = cur.fetchone()

        if row is None:

            return None

        return {
            "id": row[0],
            "filename": row[1],
            "duration_seconds": (
                float(row[2])
                if row[2] is not None
                else 0.0
            ),
            "status": row[3],
            "created_at": row[4]
        }

    finally:

        cur.close()
        conn.close()


# ============================================================
# TRANSCRIPT
# ============================================================

def get_transcript(
    meeting_id
):
    """
    Get transcript associated with a meeting.
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT
                t.id,
                t.filename,
                t.transcript_text,
                t.created_at

            FROM transcripts t

            WHERE t.meeting_id = %s

            ORDER BY t.created_at DESC

            LIMIT 1
            """,
            (meeting_id,)
        )

        row = cur.fetchone()

        if row is None:

            return None

        return {
            "id": row[0],
            "filename": row[1],
            "transcript_text": row[2],
            "created_at": row[3]
        }

    finally:

        cur.close()
        conn.close()


# ============================================================
# ANALYSIS
# ============================================================

def get_analysis(
    transcript_id
):
    """
    Get the latest analysis for a transcript.

    full_analysis is stored as TEXT in PostgreSQL,
    but the application stores structured analysis as JSON.
    This function converts it back into a Python dictionary
    when possible.
    """

    import json

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT
                id,
                transcript_id,
                themes,
                sentiment,
                summary,
                full_analysis,
                sentiment_score,
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

        # ----------------------------------------------------
        # Parse structured LLM analysis
        # ----------------------------------------------------

        full_analysis = row[5]

        if isinstance(
            full_analysis,
            str
        ):

            try:

                full_analysis = json.loads(
                    full_analysis
                )

            except (
                json.JSONDecodeError,
                TypeError
            ):

                pass

        return {
            "id": row[0],

            "transcript_id": row[1],

            "themes": row[2],

            "sentiment": row[3],

            "summary": row[4],

            "full_analysis": full_analysis,

            "sentiment_score": (
                float(row[6])
                if row[6] is not None
                else 0.0
            ),

            "created_at": row[7]
        }

    finally:

        cur.close()
        conn.close()


# ============================================================
# SPEAKER SEGMENTS
# ============================================================

def get_speaker_segments(
    transcript_id
):
    """
    Get all speaker-labelled transcript segments.
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT
                id,
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

        segments = []

        for row in rows:

            segments.append(
                {
                    "id": row[0],
                    "speaker": row[1],
                    "start": float(row[2]),
                    "end": float(row[3]),
                    "text": row[4]
                }
            )

        return segments

    finally:

        cur.close()
        conn.close()


# ============================================================
# SPEAKER ANALYTICS
# ============================================================

def get_speaker_analytics(
    transcript_id
):
    """
    Get speaker participation statistics.
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT
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

        analytics = []

        for row in rows:

            analytics.append(
                {
                    "speaker": row[0],

                    "speaking_time_seconds": float(
                        row[1]
                    ),

                    "segment_count": row[2],

                    "word_count": row[3],

                    "participation_percentage": float(
                        row[4]
                    )
                }
            )

        return analytics

    finally:

        cur.close()
        conn.close()


# ============================================================
# THEMES
# ============================================================

def get_themes(
    analysis_id
):
    """
    Get themes belonging to an analysis.
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT
                id,
                theme

            FROM themes

            WHERE analysis_id = %s

            ORDER BY id
            """,
            (analysis_id,)
        )

        return [
            {
                "id": row[0],
                "theme": row[1]
            }
            for row in cur.fetchall()
        ]

    finally:

        cur.close()
        conn.close()


# ============================================================
# KEY POINTS
# ============================================================

def get_key_points(
    analysis_id
):
    """
    Get key discussion points.
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT
                id,
                point

            FROM key_points

            WHERE analysis_id = %s

            ORDER BY id
            """,
            (analysis_id,)
        )

        return [
            {
                "id": row[0],
                "point": row[1]
            }
            for row in cur.fetchall()
        ]

    finally:

        cur.close()
        conn.close()


# ============================================================
# DECISIONS
# ============================================================

def get_decisions(
    analysis_id
):
    """
    Get decisions made during the discussion.
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT
                id,
                decision,
                speaker

            FROM decisions

            WHERE analysis_id = %s

            ORDER BY id
            """,
            (analysis_id,)
        )

        return [
            {
                "id": row[0],
                "decision": row[1],
                "speaker": row[2]
            }
            for row in cur.fetchall()
        ]

    finally:

        cur.close()
        conn.close()


# ============================================================
# ACTION ITEMS
# ============================================================

def get_action_items(
    analysis_id
):
    """
    Get action items.
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT
                id,
                task,
                speaker,
                priority

            FROM action_items

            WHERE analysis_id = %s

            ORDER BY id
            """,
            (analysis_id,)
        )

        return [
            {
                "id": row[0],
                "task": row[1],
                "speaker": row[2],
                "priority": row[3]
            }
            for row in cur.fetchall()
        ]

    finally:

        cur.close()
        conn.close()


# ============================================================
# UNRESOLVED ISSUES
# ============================================================

def get_unresolved_issues(
    analysis_id
):
    """
    Get unresolved discussion issues.
    """

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT
                id,
                issue

            FROM unresolved_issues

            WHERE analysis_id = %s

            ORDER BY id
            """,
            (analysis_id,)
        )

        return [
            {
                "id": row[0],
                "issue": row[1]
            }
            for row in cur.fetchall()
        ]

    finally:

        cur.close()
        conn.close()