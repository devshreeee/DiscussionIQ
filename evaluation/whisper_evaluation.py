from jiwer import wer

with open(
    "evaluation/ground_truth.txt",
    "r",
    encoding="utf-8"
) as file:

    ground_truth = file.read()

with open(
    "analysis/merged_transcript.txt",
    "r",
    encoding="utf-8"
) as file:

    generated = file.read()

error_rate = wer(
    ground_truth,
    generated
)

accuracy = (
    1 - error_rate
) * 100

print()
print("===== TRANSCRIPTION EVALUATION =====")
print()

print(
    f"WER: {error_rate:.4f}"
)

print(
    f"Accuracy: {accuracy:.2f}%"
)