from quiz_tts_elevenlabs import parse_quiz_sheet

url = "https://docs.google.com/spreadsheets/d/18oK50U01PLDFIUYM2rDGwMOujmDBNdOH_eA1ogzj-ko/edit?usp=sharing"

print("Running test with 2 rounds, 7 questions...")
parse_quiz_sheet(url, rounds_count=2, questions_per_round=7)
print("Test complete.")
