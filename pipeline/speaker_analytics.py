from collections import defaultdict


# ============================================================
# SPEAKER ANALYTICS
# ============================================================

def calculate_speaker_analytics(
    segments
):
    """
    Calculate speaker participation statistics.

    Expected segment format:

    {
        "speaker": "SPEAKER_00",
        "start": 0.0,
        "end": 4.5,
        "text": "Hello everyone."
    }

    Returns:

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

    if not segments:

        return []

    speaker_data = defaultdict(
        lambda: {
            "speaking_time_seconds": 0.0,
            "segment_count": 0,
            "word_count": 0
        }
    )

    # --------------------------------------------------------
    # Calculate raw statistics
    # --------------------------------------------------------

    for segment in segments:

        speaker = segment.get(
            "speaker",
            "UNKNOWN"
        )

        start = float(
            segment.get(
                "start",
                0.0
            )
        )

        end = float(
            segment.get(
                "end",
                0.0
            )
        )

        text = segment.get(
            "text",
            ""
        ).strip()

        duration = max(
            0.0,
            end - start
        )

        word_count = len(
            text.split()
        )

        speaker_data[
            speaker
        ][
            "speaking_time_seconds"
        ] += duration

        speaker_data[
            speaker
        ][
            "segment_count"
        ] += 1

        speaker_data[
            speaker
        ][
            "word_count"
        ] += word_count

    # --------------------------------------------------------
    # Total speaking time
    # --------------------------------------------------------

    total_speaking_time = sum(
        item[
            "speaking_time_seconds"
        ]
        for item in speaker_data.values()
    )

    # --------------------------------------------------------
    # Build result
    # --------------------------------------------------------

    analytics = []

    for speaker, data in speaker_data.items():

        if total_speaking_time > 0:

            participation = (
                data[
                    "speaking_time_seconds"
                ]
                /
                total_speaking_time
            ) * 100

        else:

            participation = 0.0

        analytics.append(
            {
                "speaker": speaker,

                "speaking_time_seconds": round(
                    data[
                        "speaking_time_seconds"
                    ],
                    3
                ),

                "segment_count": data[
                    "segment_count"
                ],

                "word_count": data[
                    "word_count"
                ],

                "participation_percentage": round(
                    participation,
                    3
                )
            }
        )

    # --------------------------------------------------------
    # Sort by speaking time
    # --------------------------------------------------------

    analytics.sort(
        key=lambda item: item[
            "speaking_time_seconds"
        ],
        reverse=True
    )

    return analytics


# ============================================================
# SUMMARY STATISTICS
# ============================================================

def get_speaker_summary(
    analytics
):
    """
    Generate high-level speaker statistics.
    """

    if not analytics:

        return {
            "speaker_count": 0,
            "total_speaking_time": 0.0,
            "most_active_speaker": None
        }

    total_time = sum(
        item[
            "speaking_time_seconds"
        ]
        for item in analytics
    )

    most_active = analytics[0]

    return {
        "speaker_count": len(
            analytics
        ),

        "total_speaking_time": round(
            total_time,
            3
        ),

        "most_active_speaker":
            most_active[
                "speaker"
            ]
    }