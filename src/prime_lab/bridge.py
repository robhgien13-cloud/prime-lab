"""Bridge between unverified AI proposals and approved mathematical experiments."""
from __future__ import annotations
from .verification import check, validate_spec

def assess_proposal(ai_record: dict, selected_spec: dict) -> dict:
    """Evaluate an explicitly selected template, not the AI's free-form statement.

    Important: this does NOT verify the LLM conjecture itself. A human or a
    separate constrained selector must first establish that the template
    matches the intended conjecture. Until then the AI claim is unverified.
    """
    if ai_record.get("status") != "未検証のAI提案":
        raise ValueError("Expected unverified AI proposal")
    kind, limit = validate_spec(selected_spec)
    outcome = check({"kind": kind, "limit": limit})
    return {
        "ai_proposal": ai_record,
        "template_verification": outcome,
        "ai_conjecture_verified": False,
        "link_status": "テンプレートとAI仮説の同一性は未確認",
        "explanation_for_beginners": (
            "AIの予想そのものはまだ確かめられていません。"
            "今回は関連する既知の数学的命題を、限られた範囲で計算しました。"
            + outcome["explanation"]
        ),
    }
