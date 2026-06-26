import os
import time
import logging
import traceback
import lemma_sdk

logger = logging.getLogger(__name__)

# Hard-coded fallback IDs (used when env vars are not set)
_DEFAULT_POD_ID = "019efee7-2400-75a8-9751-79f910f1bc5d"
_DEFAULT_ORG_ID = "019efee7-2093-73dc-990a-fabc1b5eec32"


class LemmaClient:
    def __init__(self, api_key=None):
        # Read credentials from environment variables first (required on Render/production).
        # Falls back to ~/.lemma/config.json (used locally after `lemma auth login`).
        token = api_key or os.environ.get("LEMMA_TOKEN")
        pod_id = os.environ.get("LEMMA_POD_ID") or _DEFAULT_POD_ID
        org_id = os.environ.get("LEMMA_ORG_ID") or _DEFAULT_ORG_ID

        logger.info(
            f"LemmaClient init: token_present={bool(token)}, "
            f"pod_id={pod_id}, org_id={org_id}"
        )

        if token:
            # Production path: token supplied via env var
            self.client = lemma_sdk.Lemma(token=token)
        else:
            # Local dev path: token loaded from ~/.lemma/config.json
            logger.info("LEMMA_TOKEN not set — falling back to ~/.lemma/config.json")
            self.client = lemma_sdk.Lemma.from_env()

        self.pod = self.client.pod(pod_id, org_id=org_id)
        logger.info("LemmaClient: pod client created successfully")

    def _run_agent_sync(self, agent_slug: str, message: str) -> str:
        start_time = time.time()
        try:
            logger.info(f"Agent {agent_slug}: starting run")
            conv = self.pod.agents.run(agent_slug, message)
            conv_id = str(conv.id)
            logger.info(f"Agent {agent_slug}: conversation started id={conv_id}")

            for attempt in range(35):  # ~52 seconds max
                time.sleep(1.5)
                try:
                    msgs = self.pod.conversations.messages(conv_id).items
                except Exception as poll_err:
                    logger.warning(
                        f"Agent {agent_slug}: poll attempt {attempt} failed: {poll_err}"
                    )
                    continue

                for m in reversed(msgs):
                    if m.role == "assistant" and m.text is not None:
                        meta = getattr(m, "metadata", None)
                        if meta:
                            props = getattr(meta, "additional_properties", {})
                            if props.get("is_final_answer"):
                                elapsed = time.time() - start_time
                                logger.info(
                                    f"Agent {agent_slug}: final_answer in {elapsed:.2f}s"
                                )
                                logger.debug(f"Agent {agent_slug} raw: {m.text!r}")
                                return m.text
                        if m.kind.value == "TEXT":
                            elapsed = time.time() - start_time
                            logger.info(
                                f"Agent {agent_slug}: TEXT response in {elapsed:.2f}s"
                            )
                            logger.debug(f"Agent {agent_slug} raw: {m.text!r}")
                            return m.text

            elapsed = time.time() - start_time
            logger.error(f"Agent {agent_slug}: timed out after {elapsed:.2f}s")

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"Agent {agent_slug}: exception after {elapsed:.2f}s: "
                f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
            )

        return "{}"

    def analyze_resume(self, text: str) -> str:
        prompt = (
            f"Analyze this resume. You MUST return ONLY valid JSON in a ```json codeblock. "
            f'Schema: {{"strengths": ["str"]}}\n\n{text}'
        )
        return self._run_agent_sync("resume-analyst", prompt)

    def analyze_jd(self, text: str) -> str:
        prompt = (
            f"Analyze this JD. You MUST return ONLY valid JSON in a ```json codeblock. "
            f'Schema: {{"company": "str", "role": "str", "required_skills": ["str"]}}\n\n{text}'
        )
        return self._run_agent_sync("jd-analyst", prompt)

    def analyze_gap(self, resume_text: str, jd_text: str) -> str:
        prompt = (
            f"Analyze the gap. You MUST return ONLY valid JSON in a ```json codeblock. "
            f'Schema: {{"missing_skills": ["str"], "suggestions": ["str"], '
            f'"strengths": ["str"], "weaknesses": ["str"], "company_fit": "str"}}\n\n'
            f"Resume:\n{resume_text}\n\nJD:\n{jd_text}"
        )
        return self._run_agent_sync("gap-analyzer", prompt)

    def score_job(self, resume_text: str, jd_text: str) -> str:
        prompt = (
            f"Score the match. You MUST return ONLY valid JSON in a ```json codeblock. "
            f'Schema: {{"score": int (0-100), "priority_level": "High|Medium|Low", '
            f'"interview_probability": int, "matched_skills": ["str"], '
            f'"missing_skills": ["str"], "reason": "str"}}\n\n'
            f"Resume:\n{resume_text}\n\nJD:\n{jd_text}"
        )
        return self._run_agent_sync("match-scorer", prompt)

    def prepare_interview(self, resume_text: str, jd_text: str) -> str:
        prompt = (
            f"Prepare interview. You MUST return ONLY valid JSON in a ```json codeblock. "
            f'Schema: {{"questions": [{{"category": "str", "difficulty": "str", '
            f'"q": "str", "company": "str"}}]}}\n\n'
            f"Resume:\n{resume_text}\n\nJD:\n{jd_text}"
        )
        return self._run_agent_sync("interview-coach", prompt)

    def generate_plan(self, gap_analysis_json: str) -> str:
        prompt = (
            f"Generate plan. You MUST return ONLY valid JSON in a ```json codeblock. "
            f'Schema: {{"today": ["str"], "this_week": ["str"]}}\n\n'
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
