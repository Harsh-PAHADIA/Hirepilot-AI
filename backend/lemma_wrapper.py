import os
import json
import logging
import httpx
import time
import traceback
import lemma_sdk
from lemma_sdk.errors import LemmaTimeoutError, LemmaAuthError

logger = logging.getLogger(__name__)

# Hard-coded fallback IDs (used when env vars are not set)
_DEFAULT_POD_ID = "019efee7-2400-75a8-9751-79f910f1bc5d"
_DEFAULT_ORG_ID = "019efee7-2093-73dc-990a-fabc1b5eec32"


class LemmaClient:
    def __init__(self, api_key=None):
        pod_id = os.environ.get("LEMMA_POD_ID") or _DEFAULT_POD_ID
        org_id = os.environ.get("LEMMA_ORG_ID") or _DEFAULT_ORG_ID
 
        token = api_key
        if not token:
            try:
                import subprocess
                # This guarantees a fresh token locally, avoiding 401s in long-running dev servers.
                # In production (Render), this may fail if CLI isn't installed, so we fallback to env var.
                token = subprocess.check_output(["lemma", "auth", "print-token"], text=True, stderr=subprocess.DEVNULL).strip()
            except Exception as e:
                logger.info(f"Could not fetch token via CLI, falling back to env var. Reason: {e}")
                token = os.environ.get("LEMMA_TOKEN")

        logger.info(
            f"LemmaClient init: token_present={bool(token)}, "
            f"pod_id={pod_id}, org_id={org_id}"
        )
        
        if token:
            self.client = lemma_sdk.Lemma(token=token, timeout=180.0)
        else:
            logger.info("LEMMA_TOKEN not set and config not found — falling back to env")
            self.client = lemma_sdk.Lemma(timeout=180.0)



        self.pod = self.client.pod(pod_id, org_id=org_id)
        logger.info("LemmaClient: pod client created successfully")

        print("=== DEBUG ===") 
        print("Token present:", bool(token))
        print("Pod ID:", pod_id)
        print("Org ID:", org_id)
        print("Pod object:", self.pod)
        print("=============")

    def _run_agent_sync(self, agent_slug: str, message: str) -> str:
        start_time = time.time()
        try:
            logger.info(f"Agent {agent_slug}: starting run")
            conv = self.pod.agents.run(agent_slug, message)
            conv_id = str(conv.id)
            logger.info(f"Agent {agent_slug}: conversation started id={conv_id}")

            last_text = None
            for attempt in range(35):  # ~52 seconds max
                time.sleep(1.5)
                try:
                    msgs = self.pod.conversations.messages(conv_id).items
                except Exception as poll_err:
                    logger.warning(
                        f"Agent {agent_slug}: poll attempt {attempt} failed: {poll_err}"
                    )
                    continue

                # Collect ALL assistant TEXT messages — combine them if there are multiple
                assistant_texts = [
                    m.text for m in msgs
                    if m.role == "assistant" and m.text and m.text.strip()
                    and m.kind.value == "TEXT"
                ]
                if assistant_texts:
                    last_text = "\n".join(assistant_texts)

                # Check if the final message is marked complete
                for m in reversed(msgs):
                    if m.role == "assistant" and m.text is not None:
                        meta = getattr(m, "metadata", None)
                        if meta:
                            props = getattr(meta, "additional_properties", {})
                            if props.get("is_final_answer"):
                                elapsed = time.time() - start_time
                                result = last_text or m.text
                                logger.info(f"Agent {agent_slug}: final_answer in {elapsed:.2f}s")
                                logger.info(f"Agent {agent_slug} raw: {result!r}")
                                return result
                        if m.kind.value == "TEXT":
                            elapsed = time.time() - start_time
                            result = last_text or m.text
                            logger.info(f"Agent {agent_slug}: TEXT response in {elapsed:.2f}s")
                            logger.info(f"Agent {agent_slug} raw: {result!r}")
                            return result

            elapsed = time.time() - start_time
            logger.error(f"Agent {agent_slug}: timed out after {elapsed:.2f}s")
            if last_text:
                logger.info(f"Agent {agent_slug}: returning partial text collected so far")
                return last_text

        except Exception as e:
            traceback.print_exc()
            raise
            # elapsed = time.time() - start_time
            # logger.error(
            #     f"Agent {agent_slug}: exception after {elapsed:.2f}s: "
            #     f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
            # )

        return "{}"

    def _send_followup(self, conv_id: str, message: str) -> None:
        """Send a follow-up message into an existing conversation."""
        try:
            self.pod.conversations.send(conv_id, message)
            logger.info(f"Follow-up sent to conv {conv_id}")
        except Exception as e:
            logger.warning(f"Failed to send follow-up: {e}")

    def _poll_for_new_reply(self, conv_id: str, after_count: int, timeout_attempts: int = 30) -> str:
        """Poll until a new TEXT message appears beyond after_count total messages."""
        for _ in range(timeout_attempts):
            time.sleep(2)
            try:
                msgs = self.pod.conversations.messages(conv_id).items
            except Exception:
                continue
            if len(msgs) > after_count:
                for m in reversed(msgs):
                    if m.role == "assistant" and m.text and m.kind.value == "TEXT":
                        logger.info(f"Follow-up reply received: {m.text[:200]!r}")
                        return m.text
        return ""

    def analyze_resume(self, text: str) -> str:

        prompt = (
            "Fill in the blanks in this JSON using the resume below. "
            "Output ONLY the completed JSON, nothing else:\n"
            '{"strengths": ["STRENGTH_1", "STRENGTH_2", "STRENGTH_3"]}\n\n'
            f"Resume:\n{text}"
        )
        return self._run_agent_sync("resume-analyst", prompt)

    def analyze_jd(self, text: str) -> str:
        prompt = (
            "Fill in the blanks in this JSON using the job description below. "
            "Output ONLY the completed JSON, nothing else:\n"
            '{"company": "COMPANY_NAME", "role": "JOB_TITLE", "required_skills": ["SKILL_1", "SKILL_2", "SKILL_3"]}\n\n'
            f"Job Description:\n{text}"
        )
        return self._run_agent_sync("jd-analyst", prompt)

    def analyze_gap(self, resume_text: str, jd_text: str) -> str:
        prompt = (
            "Fill in the blanks in this JSON by analyzing the resume against the job description. "
            "Output ONLY the completed JSON, nothing else:\n"
            '{"missing_skills": ["SKILL_1", "SKILL_2"], '
            '"suggestions": ["SUGGESTION_1", "SUGGESTION_2"], '
            '"strengths": ["STRENGTH_1", "STRENGTH_2"], '
            '"weaknesses": ["WEAKNESS_1", "WEAKNESS_2"], '
            '"company_fit": "SHORT_FIT_DESCRIPTION"}\n\n'
            f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}"
        )
        return self._run_agent_sync("gap-analyzer", prompt)

    def score_job(self, resume_text: str, jd_text: str) -> str:
        prompt = (
            "Fill in the blanks in this JSON by scoring how well the resume matches the job description. "
            "Output ONLY the completed JSON, nothing else:\n"
            '{"score": 75, "priority_level": "High", "interview_probability": 70, '
            '"matched_skills": ["SKILL_1", "SKILL_2"], '
            '"missing_skills": ["SKILL_1"], '
            '"reason": "ONE_SENTENCE_REASON"}\n\n'
            "Rules: score is 0-100, priority_level is exactly High/Medium/Low, "
            "interview_probability is 0-100.\n\n"
            f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}"
        )
        return self._run_agent_sync("match-scorer", prompt)

    def prepare_interview(self, resume_text: str, jd_text: str) -> str:
        prompt = (
            "Write exactly 5 interview questions for the candidate below. "
            "Do NOT call any tools. Do NOT generate a summary. "
            "Write the questions directly, numbered 1 to 5, one per line. "
            "Each line must follow this format exactly:\n"
            "1. [Category] ([Difficulty]): Question text here?\n"
            "Categories: Behavioral, Technical, System Design\n"
            "Difficulties: Easy, Medium, Hard\n\n"
            f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}"
        )
        start_time = time.time()
        try:
            conv = self.pod.agents.run("interview-coach", prompt)
            conv_id = str(conv.id)
            logger.info(f"interview-coach: conv started {conv_id}")

            last_text = None
            first_reply_msg_count = 0
            for attempt in range(35):
                time.sleep(1.5)
                try:
                    msgs = self.pod.conversations.messages(conv_id).items
                except Exception:
                    continue

                assistant_texts = [
                    m.text for m in msgs
                    if m.role == "assistant" and m.text and m.text.strip()
                    and m.kind.value == "TEXT"
                ]
                if assistant_texts:
                    last_text = "\n".join(assistant_texts)

                for m in reversed(msgs):
                    if m.role == "assistant" and m.text is not None:
                        meta = getattr(m, "metadata", None)
                        props = getattr(meta, "additional_properties", {}) if meta else {}
                        if props.get("is_final_answer") or m.kind.value == "TEXT":
                            result = last_text or m.text
                            elapsed = time.time() - start_time
                            logger.info(f"interview-coach: first reply in {elapsed:.2f}s: {result[:150]!r}")

                            # If the reply has questions, return it immediately
                            if '?' in result and len(result) > 50:
                                return result

                            # Agent returned a summary — send follow-up to get the actual questions
                            logger.warning("interview-coach returned summary, sending follow-up")
                            first_reply_msg_count = len(msgs)
                            self._send_followup(
                                conv_id,
                                "Now write the 5 questions out, numbered 1 to 5, one per line. "
                                "Format: 1. [Category] (Difficulty): Question text?"
                            )
                            followup_reply = self._poll_for_new_reply(
                                conv_id, first_reply_msg_count, timeout_attempts=25
                            )
                            if followup_reply:
                                logger.info(f"interview-coach follow-up reply: {followup_reply[:200]!r}")
                                return followup_reply
                            logger.error("interview-coach follow-up timed out")
                            return result  # return summary as fallback

            elapsed = time.time() - start_time
            logger.error(f"interview-coach timed out after {elapsed:.2f}s")
            return last_text or "{}"

        except Exception as e:
            import traceback
            print("=== EXCEPTION ===")
            print("Type:", type(e).__name__)
            print("Message:", e)
            traceback.print_exc()
            print("=================")
            raise
            # logger.error(f"interview-coach exception: {type(e).__name__}: {e}\n{traceback.format_exc()}")
            # return "{}"

    def generate_plan(self, gap_analysis_json: str) -> str:
        prompt = (
            "Create an action plan with exactly two sections. "
            "Write it in this exact format — no other text:\n\n"
            "Today:\n"
            "- Action item 1\n"
            "- Action item 2\n"
            "- Action item 3\n\n"
            "This Week:\n"
            "- Action item 1\n"
            "- Action item 2\n"
            "- Action item 3\n\n"
            f"Gap Analysis:\n{gap_analysis_json}"
        )
        return self._run_agent_sync("placement-planner", prompt)

    def analyze_document(self, text, doc_type="resume"):
        import json
        if doc_type == "resume":
            return json.loads(self.analyze_resume(text))
        else:
            return json.loads(self.analyze_jd(text))

    def generate_analysis(self, prompt):
        return self._run_agent_sync("gap-analyzer", prompt)
