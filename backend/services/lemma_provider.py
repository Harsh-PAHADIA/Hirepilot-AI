import json
import logging
import re
from services.ai_provider import BaseAIProvider
from lemma_wrapper import LemmaClient

logger = logging.getLogger(__name__)

AI_ERROR_MESSAGE = "AI could not generate recommendations. Please try again."


def extract_json(text: str):
    """
    Attempt to parse JSON from the AI response text.
    Returns the parsed object, or None if parsing fails.
    Logs the raw response and any parse errors.
    """
    if not text:
        logger.warning("extract_json: received empty response from AI agent")
        return None

    logger.debug(f"extract_json raw response: {text!r}")

    # Strip markdown code blocks
    match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as e:
            logger.warning(f"extract_json: failed to parse markdown block: {e}")

    # Try raw parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: find outermost { } or [ ]
    start_obj = text.find('{')
    end_obj = text.rfind('}')
    start_arr = text.find('[')
    end_arr = text.rfind(']')

    try:
        if start_obj != -1 and end_obj != -1 and (start_arr == -1 or start_obj < start_arr):
            return json.loads(text[start_obj:end_obj + 1])
        elif start_arr != -1 and end_arr != -1:
            return json.loads(text[start_arr:end_arr + 1])
    except Exception as e:
        logger.warning(f"extract_json: bracket extraction failed: {e}")

    logger.error(
        f"extract_json: could not extract any JSON from AI response. "
        f"Raw response was: {text!r}"
    )
    return None


def sanitize_list(lst):
    """Remove null, empty, or meaningless entries from an AI-returned list."""
    if not isinstance(lst, list):
        return []
    cleaned = []
    for item in lst:
        if item is None:
            continue
        val = str(item).strip()
        if val and val.lower() not in ["0", "null", "undefined", "none", "{}"]:
            cleaned.append(val)
    return cleaned


class LemmaProvider(BaseAIProvider):
    def __init__(self, api_key: str = None):
        self.client = LemmaClient(api_key=api_key)

    def analyze_jd(self, jd_text: str) -> dict:
        raw = self.client.analyze_jd(jd_text)
        data = extract_json(raw)

        if isinstance(data, dict) and ("company" in data or "required_skills" in data):
            data["required_skills"] = sanitize_list(data.get("required_skills", []))
            return data

        logger.error(f"analyze_jd: AI returned unparsable response. Raw: {raw!r}")
        return {"ai_error": AI_ERROR_MESSAGE, "company": None, "role": None, "required_skills": []}

    def analyze_gap(self, resume_text: str, jd_text: str) -> dict:
        raw = self.client.analyze_gap(resume_text, jd_text)
        data = extract_json(raw)

        if isinstance(data, dict) and ("missing_skills" in data or "suggestions" in data or "strengths" in data):
            data["missing_skills"] = sanitize_list(data.get("missing_skills", []))
            data["suggestions"] = sanitize_list(data.get("suggestions", []))
            data["strengths"] = sanitize_list(data.get("strengths", []))
            data["weaknesses"] = sanitize_list(data.get("weaknesses", []))
            return data

        logger.error(f"analyze_gap: AI returned unparsable response. Raw: {raw!r}")
        return {
            "ai_error": AI_ERROR_MESSAGE,
            "missing_skills": [],
            "suggestions": [],
            "strengths": [],
            "weaknesses": [],
            "company_fit": None,
        }

    def score_job(self, resume_text: str, jd_text: str) -> dict:
        raw = self.client.score_job(resume_text, jd_text)
        data = extract_json(raw)

        if isinstance(data, dict) and "score" in data:
            data["matched_skills"] = sanitize_list(data.get("matched_skills", []))
            data["missing_skills"] = sanitize_list(data.get("missing_skills", []))
            return data

        logger.error(f"score_job: AI returned unparsable response. Raw: {raw!r}")
        return {
            "ai_error": AI_ERROR_MESSAGE,
            "score": None,
            "priority_level": None,
            "interview_probability": None,
            "matched_skills": [],
            "missing_skills": [],
            "reason": None,
        }

    def generate_plan(self, gap_analysis: dict) -> dict:
        raw = self.client.generate_plan(json.dumps(gap_analysis))
        data = extract_json(raw)

        if isinstance(data, dict) and ("today" in data or "this_week" in data):
            data["today"] = sanitize_list(data.get("today", []))
            data["this_week"] = sanitize_list(data.get("this_week", []))
            return data

        logger.error(f"generate_plan: AI returned unparsable response. Raw: {raw!r}")
        return {"ai_error": AI_ERROR_MESSAGE, "today": [], "this_week": []}

    def prepare_interview(self, resume_text: str, jd_text: str) -> list:
        raw = self.client.prepare_interview(resume_text, jd_text)
        data = extract_json(raw)

        if isinstance(data, dict) and "questions" in data:
            questions = data.get("questions")
            if isinstance(questions, list):
                # Filter out invalid entries
                valid = [
                    q for q in questions
                    if isinstance(q, dict)
                    and q.get("question") or q.get("q")
                    and str(q.get("question", q.get("q", ""))).strip().lower()
                    not in ["0", "null", "undefined", "none", "{}"]
                ]
                return valid

        logger.error(f"prepare_interview: AI returned unparsable response. Raw: {raw!r}")
        return []
