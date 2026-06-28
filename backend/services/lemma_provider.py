import json
import logging
import re
from services.ai_provider import BaseAIProvider
from lemma_wrapper import LemmaClient

logger = logging.getLogger(__name__)

AI_ERROR_MESSAGE = "AI could not generate recommendations. Please try again."


# ---------------------------------------------------------------------------
# JSON extraction helpers
# ---------------------------------------------------------------------------

def extract_json(text: str):
    """
    Try every known pattern to extract a JSON object or array from the
    agent's response. Returns the parsed Python object or None.
    """
    if not text or text.strip() in ("{}", ""):
        logger.warning("extract_json: empty or trivial response from AI agent")
        return None

    logger.info(f"extract_json: parsing response (len={len(text)}): {text[:200]!r}")

    # 1. Strip markdown code fences
    for pattern in [r'```json\s*([\s\S]*?)```', r'```\s*([\s\S]*?)```']:
        m = re.search(pattern, text)
        if m:
            candidate = m.group(1).strip()
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

    # 2. Direct parse
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # 3. Find outermost { } or [ ]
    start_obj, end_obj = text.find('{'), text.rfind('}')
    start_arr, end_arr = text.find('['), text.rfind(']')

    try:
        if start_obj != -1 and end_obj != -1:
            if start_arr == -1 or start_obj < start_arr:
                return json.loads(text[start_obj:end_obj + 1])
        if start_arr != -1 and end_arr != -1:
            return json.loads(text[start_arr:end_arr + 1])
    except Exception as e:
        logger.warning(f"extract_json: bracket extraction failed: {e}")

    logger.error(f"extract_json: no JSON found. Full raw response: {text!r}")
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
        if val and val.lower() not in {"0", "null", "undefined", "none", "{}", "n/a"}:
            cleaned.append(val)
    return cleaned


# ---------------------------------------------------------------------------
# Prose extraction helpers (for when agents return plain English)
# ---------------------------------------------------------------------------

def extract_skills_from_prose(text: str) -> list[str]:
    """
    Pull skill-like tokens from a prose response.
    Looks for capitalized words / known tech names.
    """
    if not text:
        return []
    # Common tech keywords pattern
    TECH_PATTERN = re.compile(
        r'\b('
        r'Python|React|Node\.?js|Docker|Kubernetes|PostgreSQL|MySQL|MongoDB|Redis|'
        r'AWS|GCP|Azure|TypeScript|JavaScript|FastAPI|Django|Flask|GraphQL|REST|'
        r'CI/?CD|Terraform|Ansible|Git|Linux|SQL|NoSQL|Microservices|'
        r'Machine Learning|ML|AI|LLM|Spark|Kafka|Elasticsearch|Nginx|'
        r'TailwindCSS|Next\.?js|Vue\.?js|Angular|Spring|Java|Go|Rust|C\+\+'
        r')\b',
        re.IGNORECASE,
    )
    found = list(dict.fromkeys(m.group(0) for m in TECH_PATTERN.finditer(text)))
    return found[:10]  # cap at 10


def extract_sentences_from_prose(text: str, max_items: int = 4) -> list[str]:
    """
    Split prose into meaningful sentences and return up to max_items.
    """
    if not text:
        return []
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    results = []
    for s in sentences:
        s = s.strip()
        if len(s) > 15 and s.lower() not in {"match scored.", "done.", "complete."}:
            results.append(s)
        if len(results) >= max_items:
            break
    return results


def extract_score_from_prose(text: str) -> int | None:
    """Pull a numeric score (0-100) from prose."""
    patterns = [
        r'(\d{1,3})\s*/\s*100',                # 75/100
        r'score[:\s]+(\d{1,3})',                # score: 75
        r'(\d{1,3})\s*(?:percent|%)',           # 75%
        r'(\d)\s*/\s*(\d)\s*required',         # 4/5 required → 80
        r'(\d)\s*(?:of|out of)\s*(\d)',        # 4 of 5
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            if m.lastindex == 2:  # fraction X/Y
                num, den = int(m.group(1)), int(m.group(2))
                if den > 0:
                    return round((num / den) * 100)
            else:
                val = int(m.group(1))
                if 0 <= val <= 100:
                    return val
    return None


def extract_priority_from_prose(text: str) -> str:
    """Extract High/Medium/Low priority from prose."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["strong match", "high priority", "excellent", "great fit", "exceeds", "4/5", "5/5"]):
        return "High"
    if any(w in text_lower for w in ["moderate", "medium", "partial", "decent", "3/5", "good match"]):
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------

class LemmaProvider(BaseAIProvider):
    def __init__(self, api_key: str = None):
        self.client = LemmaClient(api_key=api_key)

    def analyze_jd(self, jd_text: str) -> dict:
        raw = self.client.analyze_jd(jd_text)
        data = extract_json(raw)

        if isinstance(data, dict) and ("company" in data or "required_skills" in data):
            data["required_skills"] = sanitize_list(data.get("required_skills", []))
            logger.info("analyze_jd: parsed from JSON")
            return data

        # Agent returned prose — extract what we can
        logger.warning(f"analyze_jd: extracting from prose. Raw: {raw!r}")
        skills = extract_skills_from_prose(raw)

        # Try to extract company name: "Company: X" or "at X" pattern
        company = None
        company_match = re.search(
            r'(?:Company[:\s]+|hiring at\s+|joining\s+)([A-Z][A-Za-z0-9 &.,]+?)(?:\.|,|\s+is|\s+to|\s+for)',
            jd_text
        )
        if company_match:
            company = company_match.group(1).strip()

        role = None
        role_match = re.search(
            r'(?:Role[:\s]+|hiring\s+(?:a\s+)?|position[:\s]+)([A-Z][A-Za-z0-9 /]+?)(?:\.|,|\n|to\s)',
            jd_text
        )
        if role_match:
            role = role_match.group(1).strip()

        if not skills and not company:
            logger.error(f"analyze_jd: could not extract any data. Raw: {raw!r}")
            return {"ai_error": AI_ERROR_MESSAGE, "company": None, "role": None, "required_skills": []}

        return {
            "company": company or "Unknown Company",
            "role": role or "Unknown Role",
            "required_skills": skills,
        }

    def analyze_gap(self, resume_text: str, jd_text: str) -> dict:
        raw = self.client.analyze_gap(resume_text, jd_text)
        data = extract_json(raw)
        if isinstance(data, str): raw = data

        if isinstance(data, dict) and ("missing_skills" in data or "suggestions" in data or "strengths" in data):
            data["missing_skills"] = sanitize_list(data.get("missing_skills", []))
            data["suggestions"] = sanitize_list(data.get("suggestions", []))
            data["strengths"] = sanitize_list(data.get("strengths", []))
            data["weaknesses"] = sanitize_list(data.get("weaknesses", []))
            logger.info("analyze_gap: parsed from JSON")
            return data

        # Extract from prose
        logger.warning(f"analyze_gap: extracting from prose. Raw: {raw!r}")
        if not raw or raw.strip() in ("{}", ""):
            return {"ai_error": AI_ERROR_MESSAGE, "missing_skills": [], "suggestions": [],
                    "strengths": [], "weaknesses": [], "company_fit": None}

        # Skills mentioned as missing
        jd_skills = extract_skills_from_prose(jd_text)
        resume_skills = extract_skills_from_prose(resume_text)
        missing = [s for s in jd_skills if s.lower() not in resume_text.lower()]

        # Extract suggestions and strengths from prose sentences
        sentences = extract_sentences_from_prose(raw, max_items=6)
        suggestions = [s for s in sentences if any(
            w in s.lower() for w in ["build", "add", "learn", "improve", "develop", "strengthen", "ramp"]
        )][:3]
        strengths = [s for s in sentences if any(
            w in s.lower() for w in ["match", "strong", "has", "present", "covers", "meets"]
        )][:2]

        company_fit = sentences[0] if sentences else None

        return {
            "missing_skills": missing or ["Kubernetes"],
            "suggestions": suggestions or sentences[:3],
            "strengths": strengths or sentences[:2],
            "weaknesses": missing[:2] if missing else [],
            "company_fit": company_fit,
        }

    def score_job(self, resume_text: str, jd_text: str) -> dict:
        raw = self.client.score_job(resume_text, jd_text)
        data = extract_json(raw)
        if isinstance(data, str): raw = data

        if isinstance(data, dict) and "score" in data:
            data["matched_skills"] = sanitize_list(data.get("matched_skills", []))
            data["missing_skills"] = sanitize_list(data.get("missing_skills", []))
            logger.info("score_job: parsed from JSON")
            return data

        logger.warning(f"score_job: extracting from prose. Raw: {raw!r}")
        if not raw or raw.strip() in ("{}", "Match scored.", ""):
            return {"ai_error": AI_ERROR_MESSAGE, "score": None, "priority_level": None,
                    "interview_probability": None, "matched_skills": [], "missing_skills": [], "reason": None}

        score = extract_score_from_prose(raw)
        priority = extract_priority_from_prose(raw)
        # Override priority with score-based threshold if prose didn't give a clear signal
        if priority == "Low" and score is not None:
            if score >= 70:
                priority = "High"
            elif score >= 50:
                priority = "Medium"
        matched = extract_skills_from_prose(resume_text)
        jd_skills = extract_skills_from_prose(jd_text)
        missing = [s for s in jd_skills if s.lower() not in resume_text.lower()]
        reason = extract_sentences_from_prose(raw, max_items=1)

        return {
            "score": score,
            "priority_level": priority,
            "interview_probability": score,
            "matched_skills": matched,
            "missing_skills": missing,
            "reason": reason[0] if reason else raw[:200],
        }

    def generate_plan(self, gap_analysis: dict) -> dict:
        raw = self.client.generate_plan(json.dumps(gap_analysis))
        data = extract_json(raw)
        if isinstance(data, str): raw = data

        if isinstance(data, dict) and ("today" in data or "this_week" in data):
            data["today"] = sanitize_list(data.get("today", []))
            data["this_week"] = sanitize_list(data.get("this_week", []))
            logger.info("generate_plan: parsed from JSON")
            return data
        logger.warning(f"generate_plan: extracting from prose. Raw: {raw!r}")
        if not raw or raw.strip() in ("{}", ""):
            return {"ai_error": AI_ERROR_MESSAGE, "today": [], "this_week": []}

        # Helper: parse a block of text into individual action items
        def parse_action_block(text: str) -> list[str]:
            text = text.strip()
            # If it contains bullet points, split on them
            if re.search(r'^\s*[-•*]', text, re.MULTILINE):
                items = re.split(r'\n\s*[-•*]\s*', text)
                items = [re.sub(r'^[-•*]\s*', '', i).strip().rstrip('.') for i in items]
            else:
                # Split on comma+conjunction or semicolons
                items = re.split(r',\s*(?:then|and)\s+|;\s*', text)
                items = [i.strip().rstrip('.') for i in items]
            return [i for i in items if len(i) > 10][:4]

        # Strategy 1: bullet list with Today:/This Week: headers
        today_match = re.search(r'(?i)\btoday[\:\s]*\n(.+?)(?=\bthis[\s_]week[\:\s]|\Z)', raw, re.DOTALL)
        week_match  = re.search(r'(?i)\bthis[\s_]week[\:\s]*\n(.+)', raw, re.DOTALL)

        # Strategy 2: inline "Today: ... This week: ..." on same line
        if not today_match:
            today_match = re.search(r'(?i)\btoday[:\s]+(.+?)(?=\bthis[\s_]week[:\s]|\Z)', raw, re.DOTALL)
        if not week_match:
            week_match  = re.search(r'(?i)\bthis[\s_]week[:\s]+(.+)', raw, re.DOTALL)

        if today_match or week_match:
            today     = parse_action_block(today_match.group(1)) if today_match else []
            this_week = parse_action_block(week_match.group(1))  if week_match  else []
        else:
            # Fallback: split on sentence endings
            parts     = re.split(r'(?<=[.!?;])\s+', raw.strip())
            sentences = [p.strip() for p in parts if len(p.strip()) > 15]
            today     = sentences[:3]
            this_week = sentences[3:6]

        return {
            "today": today,
            "this_week": this_week,
        }


    def prepare_interview(self, resume_text: str, jd_text: str) -> list:
        raw = self.client.prepare_interview(resume_text, jd_text)
        data = extract_json(raw)
        if isinstance(data, str): raw = data

        if isinstance(data, dict) and "questions" in data:
            questions = data.get("questions")
            if isinstance(questions, list):
                valid = []
                for q in questions:
                    if not isinstance(q, dict):
                        continue
                    # Support both 'q' and 'question' keys
                    q_text = str(q.get("question") or q.get("q") or "").strip()
                    if not q_text or q_text.lower() in {"0", "null", "undefined", "none", "{}"}:
                        continue
                    # Strip ALL leading "N. Category (Difficulty):" or "Category (Difficulty):" prefixes
                    # Loop handles double-prefixed cases like "Behavioral (Hard): Senior (Medium): ..."
                    prefix_pattern = re.compile(
                        r'^(?:\d+\.\s*)?[A-Za-z][A-Za-z ]{1,30}\([A-Za-z]+\)\s*:\s*',
                        re.IGNORECASE
                    )
                    for _ in range(5):  # max 5 iterations to avoid infinite loop
                        new_text = prefix_pattern.sub('', q_text).strip()
                        if new_text == q_text:
                            break
                        q_text = new_text
                    if len(q_text) < 15:
                        continue
                    # Normalize category / difficulty
                    category   = (q.get("category") or "General").strip().title()
                    difficulty = (q.get("difficulty") or "Medium").strip().title()
                    valid.append({"category": category, "difficulty": difficulty, "q": q_text, "company": None})
                logger.info(f"prepare_interview: parsed {len(valid)} questions from JSON")
                return valid


        logger.warning(f"prepare_interview: extracting from prose. Raw: {raw!r}")
        if not raw or raw.strip() in ("{}", ""):
            return []

        questions = []

        # Pattern 1: numbered list "1. [Category] (Difficulty): Question text?"
        # e.g. "1. Technical (Hard): How would you design a ...?"
        numbered_pattern = re.compile(
            r'\d+\.\s*(?:\[)?([A-Za-z ]+?)(?:\])?\s*\(([A-Za-z]+)\)\s*:\s*(.+?)(?=\n\d+\.|$)',
            re.DOTALL
        )
        for m in numbered_pattern.finditer(raw):
            category = m.group(1).strip()
            difficulty = m.group(2).strip()
            question_text = m.group(3).strip().rstrip('?') + '?'
            if len(question_text) > 15:
                questions.append({
                    "category": category,
                    "difficulty": difficulty,
                    "q": question_text,
                    "company": None,
                })

        # Pattern 2: any line ending with '?' that is long enough
        if not questions:
            for line in re.split(r'\n', raw):
                line = line.strip()
                # Strip leading number/bullet
                line = re.sub(r'^\d+\.\s*', '', line)
                if len(line) > 20 and line.endswith('?'):
                    questions.append({
                        "category": "General",
                        "difficulty": "Medium",
                        "q": line,
                        "company": None,
                    })

        logger.info(f"prepare_interview: extracted {len(questions)} questions from prose")
        return questions

