"""
HR Policy Agent - Performance Evaluation (Scenarios 1-6)
Course: 24CSEN4121 - Building Agentic AI Systems
"""

import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def calculate_metrics():
    # Scenario 1: Baseline Success & Failure Rates
    total_q = 200
    success_q = 184
    failed_q = total_q - success_q
    success_rate = (success_q / total_q) * 100.0
    failure_rate = (failed_q / total_q) * 100.0

    # Scenario 2: Target Improvement (+6 to hit 95%)
    target_rate = 95.0
    needed_success = int(round(total_q * (target_rate / 100.0)))
    additional_needed = needed_success - success_q

    # Scenario 3: Factual Accuracy & Hallucination Rate
    checked_claims = 250
    errors = 8
    hallucination_rate = (errors / checked_claims) * 100.0
    factual_accuracy = 100.0 - hallucination_rate
    extended_claims = 500
    max_error_pct = 2.0
    max_allowed_errors = int(round(extended_claims * (max_error_pct / 100.0)))

    # Scenario 4: Cost Analysis
    in_tokens = 2000
    out_tokens = 500
    commercial_cost = (in_tokens * 0.001) + (out_tokens * 0.002)

    # Scenario 5: Multi-Step Chained Reliability (4 steps at 95%)
    steps = 4
    step_rate = 0.95
    chained_reliability = (step_rate ** steps) * 100.0

    return {
        "s1": {"total": total_q, "success": success_q, "failed": failed_q, "rate": success_rate, "fail_rate": failure_rate},
        "s2": {"needed": needed_success, "additional": additional_needed},
        "s3": {"hallucination": hallucination_rate, "accuracy": factual_accuracy, "max_errors": max_allowed_errors},
        "s4": {"commercial": commercial_cost, "local": 0.00},
        "s5": {"chained_rel": chained_reliability},
    }


def print_report():
    m = calculate_metrics()
    print("=" * 75)
    print("  HR POLICY AGENT — PERFORMANCE EVALUATION REPORT")
    print("=" * 75 + "\n")

    print(f"1. BASELINE PERFORMANCE:")
    print(f"   • Success Rate        : {m['s1']['rate']:.1f}% ({m['s1']['success']}/{m['s1']['total']})")
    print(f"   • Failure Rate        : {m['s1']['fail_rate']:.1f}%\n")

    print(f"2. TARGET IMPROVEMENT:")
    print(f"   • Goal: 95% (Need +{m['s2']['additional']} more answers)\n")

    print(f"3. FACTUAL ACCURACY:")
    print(f"   • Hallucination Rate  : {m['s3']['hallucination']:.1f}%")
    print(f"   • Factual Accuracy    : {m['s3']['accuracy']:.1f}%\n")

    print(f"4. COST:")
    print(f"   • Commercial API      : ${m['s4']['commercial']:.2f}/query")
    print(f"   • Local Ollama        : $0.00 (Free)\n")

    print(f"5. PIPELINE RELIABILITY:")
    print(f"   • 4-Step Chain        : {m['s5']['chained_rel']:.1f}%\n")

    print(f"6. SUMMARY:")
    print(f"   • Meets Target        : Success Rate 92% (baseline OK)")
    print(f"   • Needs Work          : Hallucination 3.2% > 2% limit")
    print(f"   • Action              : Strengthen prompt guardrails\n")
    print("=" * 75)


if __name__ == "__main__":
    print_report()
