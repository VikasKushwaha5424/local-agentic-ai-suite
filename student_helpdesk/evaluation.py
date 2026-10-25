"""
AI Student Helpdesk - Evaluation Suite
Course: 24CSEN4121 - Building Agentic AI Systems
"""

import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from cli import init_engine, ask

TEST_CASES = [
    {
        "id": 1,
        "query": "What is the procedure for applying for a bonafide certificate?",
        "expected_keywords": ["bonafide", "portal", "100", "room 102"],
    },
    {
        "id": 2,
        "query": "What are the library timings and borrowing rules?",
        "expected_keywords": ["8:00 am", "9:00 pm", "4 books", "14 days"],
    },
    {
        "id": 3,
        "query": "What attendance percentage is required, and what happens below 65%?",
        "expected_keywords": ["75%", "65%", "debarred"],
    },
    {
        "id": 4,
        "query": "Explain the grading system and minimum CGPA needed for graduation.",
        "expected_keywords": ["grade", "cgpa", "5.0"],
    },
]


def run_evaluation():
    print("=" * 70)
    print(" AI STUDENT HELPDESK — EVALUATION SUITE")
    print("=" * 70 + "\n")
    index, qa_chain = init_engine()

    passed = 0
    total = len(TEST_CASES)

    for case in TEST_CASES:
        qid = case["id"]
        q = case["query"]
        print(f"[{qid}/{total}] Testing: \"{q}\"")
        t0 = time.time()
        ans = ask(index, qa_chain, q)
        elapsed = time.time() - t0

        ans_lower = ans.lower()
        matches = [kw for kw in case["expected_keywords"] if kw.lower() in ans_lower]
        is_pass = len(matches) >= 2

        if is_pass:
            passed += 1
            print(f"       Status: PASS | Matched Keywords: {matches} | Time: {elapsed:.2f}s\n")
        else:
            print(f"       Status: REVIEW | Matched: {matches} | Time: {elapsed:.2f}s\n")

    accuracy = (passed / total) * 100.0
    print("=" * 70)
    print(f" EVALUATION SUMMARY: {passed}/{total} Passed ({accuracy:.1f}% Accuracy)")
    print("=" * 70)


if __name__ == "__main__":
    run_evaluation()
