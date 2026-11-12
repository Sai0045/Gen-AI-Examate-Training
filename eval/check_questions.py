from app.records import load_records
from app.smart_search import SmartSearch

questions = [
    "My baby is 7 weeks old and missed the 6-week session. Is it too late for the 6-week vaccines?",
    "Which vaccines are due at 6 weeks?",
    "Which vaccines are given at birth?",
    "Where is the Hepatitis B birth dose given?",
    "What is the BCG dose after the baby is one month old?",
    "Is paracetamol safe for my baby after the vaccine?",
    "Until what age can Pentavalent be given?",
    "When is the first Measles Rubella dose given?",
    "When is the first Vitamin A dose and how much is given?",
    "Which vaccine do pregnant women get and when?",
]

engine = SmartSearch(load_records())

number = 1
for q in questions:
    results = engine.search(q, top_k=1)
    print("Q" + str(number) + ":", q)
    if len(results) == 0 or results[0]["score"] < 0.1:
        print("    -> I don't know")
    else:
        print("    ->", results[0]["vaccine"], "(score", results[0]["score"], ")")
    number = number + 1
