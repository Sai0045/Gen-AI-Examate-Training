from datetime import date

from app.chat import parse_json
from app.llm import ask_llm
from app.rag import answer_question
from app.tools import vaccine_due_dates

AGENT_SYSTEM_PROMPT = """
You are a tool-selection agent for TeekaTimer, an Indian immunization
schedule assistant.

Choose exactly one tool based on the user's request.

Available tools:

1. search_mohfw_documents
   Use for questions about vaccine facts, doses, timing, eligibility,
   routes, vaccine-preventable diseases, and official immunization guidance.

2. calculate_vaccine_calendar
   Use when the user asks for a personal vaccine schedule, due dates,
   missed doses, or vaccine status for a baby.

Return only valid JSON.

For document questions, use this format:
{
  "tool": "search_mohfw_documents",
  "query": "the user's question"
}

For personal vaccine calendars, use this format:
{
  "tool": "calculate_vaccine_calendar",
  "date_of_birth": "YYYY-MM-DD"
}

Rules:
- Extract the date of birth only if the user explicitly provides it.
- Never invent a date of birth.
- If the date of birth is missing, return:
  {"tool": "calculate_vaccine_calendar", "date_of_birth": null}
- Do not answer the user's medical question yourself.
- Do not return Markdown or explanations outside the JSON.
"""


def select_tool(user_message):
    """Ask the LLM which tool should handle the request."""
    response = ask_llm(
        AGENT_SYSTEM_PROMPT,
        user_message,
        temperature=0
    )

    decision = parse_json(response)

    if not isinstance(decision, dict):
        raise TypeError("The agent returned an invalid tool selection.")

    tool_name = decision.get("tool")

    if tool_name not in (
        "search_mohfw_documents",
        "calculate_vaccine_calendar"
    ):
        raise RuntimeError("The agent selected an unsupported tool.")

    return decision


def execute_tool(decision, original_question):
    """Validate and execute the selected tool."""

    tool_name = decision["tool"]

    if tool_name == "search_mohfw_documents":
        query = str(decision.get("query") or original_question).strip()

        if not query:
            raise ValueError("A search question is required.")

        result = answer_question(query)

        return {
            "tool": tool_name,
            "answer": result["answer"],
            "answerable": result["answerable"],
            "citations": result["citations"],
            "retrieved": result["retrieved"],
        }

    if tool_name == "calculate_vaccine_calendar":
        dob = decision.get("date_of_birth")

        if not dob:
            return {
                "tool": tool_name,
                "needs_input": True,
                "answer": "Please provide the baby's date of birth in YYYY-MM-DD format.",
                "calendar": None,
            }

        # Validate the date before running the calculator.
        try:
            date.fromisoformat(str(dob))
        except ValueError:
            return {
                "tool": tool_name,
                "needs_input": True,
                "answer": "Please provide a valid date of birth in YYYY-MM-DD format.",
                "calendar": None,
            }

        result = vaccine_due_dates(date_of_birth=str(dob))

        status_counts = {}
        for dose in result["doses"]:
            status = dose["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "tool": tool_name,
            "answer": (
                "The vaccine calendar has been calculated successfully. "
                "Total scheduled doses: " + str(result["total_doses"])
            ),
            "date_of_birth": result["date_of_birth"],
            "today": result["today"],
            "total_doses": result["total_doses"],
            "status_counts": status_counts,
            "doses": result["doses"],
        }

    raise RuntimeError("Unsupported tool.")


def run_agent(user_message):
    """
    Hand-written agent loop:
    1. Receive the user's request.
    2. Ask the LLM to select a tool.
    3. Execute the selected Python tool.
    4. Return the tool result.
    """
    question = str(user_message).strip()

    if not question:
        raise ValueError("Please enter a question.")

    decision = select_tool(question)
    result = execute_tool(decision, question)

    return result
