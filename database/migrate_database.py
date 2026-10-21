from database.db_connection import get_connection


# ============================================================
# DATABASE MIGRATION
# ============================================================

def column_exists(
    cursor,
    table_name,
    column_name
):
    """
    Check whether a column already exists in a table.
    """

    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = %s
            AND column_name = %s
        );
        """,
        (
            table_name,
            column_name
        )
    )

    return cursor.fetchone()[0]


def table_exists(
    cursor,
    table_name
):
    """
    Check whether a table already exists.
    """

    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = %s
        );
        """,
        (table_name,)
    )

    return cursor.fetchone()[0]


def add_column_if_missing(
    cursor,
    table_name,
    column_name,
    column_definition
):
    """
    Add a column only if it doesn't already exist.
    """

    if not column_exists(
        cursor,
        table_name,
        column_name
    ):

        cursor.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name}
            {column_definition};
            """
        )

        print(
            f"  ✓ Added {table_name}.{column_name}"
        )

    else:

        print(
            f"  • {table_name}.{column_name} already exists"
        )


def create_table_if_missing(
    cursor,
    table_name,
    create_statement
):
    """
    Create a table only if it doesn't already exist.
    """

    if not table_exists(
        cursor,
        table_name
    ):

        cursor.execute(
            create_statement
        )

        print(
            f"  ✓ Created table {table_name}"
        )

    else:

        print(
            f"  • Table {table_name} already exists"
        )


def migrate_database():

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            print()
            print("=" * 60)
            print("DiscussionIQ Database Migration")
            print("=" * 60)
            print()

            # ==================================================
            # TRANSCRIPTS
            # ==================================================

            print("Checking transcripts...")

            add_column_if_missing(
                cur,
                "transcripts",
                "meeting_id",
                "INTEGER"
            )

            # ==================================================
            # SPEAKER SEGMENTS
            # ==================================================

            print()
            print("Checking speaker segments...")

            add_column_if_missing(
                cur,
                "speaker_segments",
                "text",
                "TEXT"
            )

            # ==================================================
            # ANALYSES
            # ==================================================

            print()
            print("Checking analyses...")

            add_column_if_missing(
                cur,
                "analyses",
                "sentiment_score",
                "NUMERIC(6,4)"
            )

            # ==================================================
            # MEETINGS
            # ==================================================

            print()
            print("Checking meetings table...")

            create_table_if_missing(
                cur,
                "meetings",
                """
                CREATE TABLE meetings (

                    id SERIAL PRIMARY KEY,

                    filename VARCHAR(255) NOT NULL,

                    duration_seconds NUMERIC(12,3),

                    status VARCHAR(30)
                        DEFAULT 'completed',

                    created_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # ==================================================
            # THEMES
            # ==================================================

            print()
            print("Checking themes table...")

            create_table_if_missing(
                cur,
                "themes",
                """
                CREATE TABLE themes (

                    id SERIAL PRIMARY KEY,

                    analysis_id INTEGER NOT NULL
                        REFERENCES analyses(id)
                        ON DELETE CASCADE,

                    theme TEXT NOT NULL,

                    created_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # ==================================================
            # KEY POINTS
            # ==================================================

            print()
            print("Checking key_points table...")

            create_table_if_missing(
                cur,
                "key_points",
                """
                CREATE TABLE key_points (

                    id SERIAL PRIMARY KEY,

                    analysis_id INTEGER NOT NULL
                        REFERENCES analyses(id)
                        ON DELETE CASCADE,

                    point TEXT NOT NULL,

                    created_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # ==================================================
            # DECISIONS
            # ==================================================

            print()
            print("Checking decisions table...")

            create_table_if_missing(
                cur,
                "decisions",
                """
                CREATE TABLE decisions (

                    id SERIAL PRIMARY KEY,

                    analysis_id INTEGER NOT NULL
                        REFERENCES analyses(id)
                        ON DELETE CASCADE,

                    decision TEXT NOT NULL,

                    speaker VARCHAR(100),

                    created_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # ==================================================
            # ACTION ITEMS
            # ==================================================

            print()
            print("Checking action_items table...")

            create_table_if_missing(
                cur,
                "action_items",
                """
                CREATE TABLE action_items (

                    id SERIAL PRIMARY KEY,

                    analysis_id INTEGER NOT NULL
                        REFERENCES analyses(id)
                        ON DELETE CASCADE,

                    task TEXT NOT NULL,

                    speaker VARCHAR(100),

                    priority VARCHAR(30),

                    status VARCHAR(30)
                        DEFAULT 'pending',

                    created_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # ==================================================
            # UNRESOLVED ISSUES
            # ==================================================

            print()
            print("Checking unresolved_issues table...")

            create_table_if_missing(
                cur,
                "unresolved_issues",
                """
                CREATE TABLE unresolved_issues (

                    id SERIAL PRIMARY KEY,

                    analysis_id INTEGER NOT NULL
                        REFERENCES analyses(id)
                        ON DELETE CASCADE,

                    issue TEXT NOT NULL,

                    created_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # ==================================================
            # SPEAKER ANALYTICS
            # ==================================================

            print()
            print("Checking speaker_analytics table...")

            create_table_if_missing(
                cur,
                "speaker_analytics",
                """
                CREATE TABLE speaker_analytics (

                    id SERIAL PRIMARY KEY,

                    transcript_id INTEGER NOT NULL
                        REFERENCES transcripts(id)
                        ON DELETE CASCADE,

                    speaker VARCHAR(100) NOT NULL,

                    speaking_time_seconds NUMERIC(12,3),

                    segment_count INTEGER,

                    word_count INTEGER,

                    participation_percentage NUMERIC(6,3),

                    created_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # ==================================================
            # MODEL EVALUATIONS
            # ==================================================

            print()
            print("Checking model_evaluations table...")

            create_table_if_missing(
                cur,
                "model_evaluations",
                """
                CREATE TABLE model_evaluations (

                    id SERIAL PRIMARY KEY,

                    transcript_id INTEGER
                        REFERENCES transcripts(id)
                        ON DELETE CASCADE,

                    wer NUMERIC(8,6),

                    accuracy_percentage NUMERIC(8,4),

                    evaluation_type VARCHAR(100),

                    created_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # ==================================================
            # FOREIGN KEY: TRANSCRIPTS → MEETINGS
            # ==================================================

            print()
            print("Checking transcript → meeting relationship...")

            cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.table_constraints
                    WHERE constraint_name =
                        'transcripts_meeting_id_fkey'
                    AND table_name = 'transcripts'
                );
                """
            )

            fk_exists = cur.fetchone()[0] # type: ignore

            if not fk_exists:

                cur.execute(
                    """
                    ALTER TABLE transcripts
                    ADD CONSTRAINT transcripts_meeting_id_fkey
                    FOREIGN KEY (meeting_id)
                    REFERENCES meetings(id)
                    ON DELETE CASCADE;
                    """
                )

                print(
                    "  ✓ Added transcripts → meetings relationship"
                )

            else:

                print(
                    "  • transcripts → meetings relationship already exists"
                )

            # ==================================================
            # INDEXES
            # ==================================================

            print()
            print("Creating indexes...")

            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_transcripts_created_at
                ON transcripts(created_at);
                """
            )

            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_transcripts_meeting_id
                ON transcripts(meeting_id);
                """
            )

            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_speaker_segments_transcript
                ON speaker_segments(transcript_id);
                """
            )

            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_speaker_segments_speaker
                ON speaker_segments(speaker);
                """
            )

            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_analyses_transcript
                ON analyses(transcript_id);
                """
            )

            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_themes_analysis
                ON themes(analysis_id);
                """
            )

            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_action_items_analysis
                ON action_items(analysis_id);
                """
            )

            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_decisions_analysis
                ON decisions(analysis_id);
                """
            )

            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_evaluations_transcript
                ON model_evaluations(transcript_id);
                """
            )

            print(
                "  ✓ Indexes ready"
            )

        # ======================================================
        # COMMIT
        # ======================================================

        conn.commit()

        print()
        print("=" * 60)
        print("✅ DATABASE MIGRATION COMPLETED")
        print("=" * 60)
        print()

    except Exception as e:

        conn.rollback()

        print()
        print("❌ DATABASE MIGRATION FAILED")
        print()
        print(e)

        raise

    finally:

        conn.close()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    migrate_database()