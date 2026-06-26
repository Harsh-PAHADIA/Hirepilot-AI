import time
import lemma_sdk

class LemmaClient:
    def __init__(self, api_key=None):
        self.client = lemma_sdk.Lemma.from_env()
        pod_id = self.client.settings.pod_id or "019efee7-2400-75a8-9751-79f910f1bc5d"
        org_id = self.client.settings.org_id or "019efee7-2093-73dc-990a-fabc1b5eec32"
        self.pod = self.client.pod(pod_id, org_id=org_id)

    def _run_agent_sync(self, agent_slug: str, message: str) -> str:
        import time
        start_time = time.time()
        try:
            conv = self.pod.agents.run(agent_slug, message)
            conv_id = str(conv.id)
            
            for _ in range(35): # ~50 seconds max
                time.sleep(1.5)
                msgs = self.pod.conversations.messages(conv_id).items
                for m in reversed(msgs):
                    if m.role == 'assistant' and m.text is not None:
                        meta = getattr(m, 'metadata', None)
                        if meta:
                            props = getattr(meta, 'additional_properties', {})
                            if props.get('is_final_answer'):
                                elapsed = time.time() - start_time
                                print(f"Agent {agent_slug} completed in {elapsed:.2f}s")
                                print(f"Raw: {m.text}")
                                return m.text
                        if m.kind.value == 'TEXT':
                            elapsed = time.time() - start_time
                            print(f"Agent {agent_slug} completed in {elapsed:.2f}s")
                            print(f"Raw: {m.text}")
                            return m.text
            elapsed = time.time() - start_time
            print(f"Agent {agent_slug} timed out after {elapsed:.2f}s")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"Agent {agent_slug} error after {elapsed:.2f}s: {e}")
            pass
            
        return "{}"

    def analyze_resume(self, text: str) -> str:
        prompt = f"Analyze this resume. You MUST return ONLY valid JSON in a ```json codeblock. Schema: {{\"strengths\": [\"str\"]}}\n\n{text}"
        return self._run_agent_sync("resume-analyst", prompt)

    def analyze_jd(self, text: str) -> str:
        prompt = f"Analyze this JD. You MUST return ONLY valid JSON in a ```json codeblock. Schema: {{\"company\": \"str\", \"role\": \"str\", \"required_skills\": [\"str\"]}}\n\n{text}"
        return self._run_agent_sync("jd-analyst", prompt)

    def analyze_gap(self, resume_text: str, jd_text: str) -> str:
        prompt = f"Analyze the gap. You MUST return ONLY valid JSON in a ```json codeblock. Schema: {{\"missing_skills\": [\"str\"], \"suggestions\": [\"str\"], \"strengths\": [\"str\"], \"weaknesses\": [\"str\"], \"company_fit\": \"str\"}}\n\nResume:\n{resume_text}\n\nJD:\n{jd_text}"
        return self._run_agent_sync("gap-analyzer", prompt)

    def score_job(self, resume_text: str, jd_text: str) -> str:
        prompt = f"Score the match. You MUST return ONLY valid JSON in a ```json codeblock. Schema: {{\"score\": int (0-100), \"priority_level\": \"High|Medium|Low\", \"interview_probability\": int, \"matched_skills\": [\"str\"], \"missing_skills\": [\"str\"], \"reason\": \"str\"}}\n\nResume:\n{resume_text}\n\nJD:\n{jd_text}"
        return self._run_agent_sync("match-scorer", prompt)

    def prepare_interview(self, resume_text: str, jd_text: str) -> str:
        prompt = f"Prepare interview. You MUST return ONLY valid JSON in a ```json codeblock. Schema: {{\"questions\": [{{\"category\": \"str\", \"difficulty\": \"str\", \"q\": \"str\", \"company\": \"str\"}}]}}\n\nResume:\n{resume_text}\n\nJD:\n{jd_text}"
        return self._run_agent_sync("interview-coach", prompt)

    def generate_plan(self, gap_analysis_json: str) -> str:
        prompt = f"Generate plan. You MUST return ONLY valid JSON in a ```json codeblock. Schema: {{\"today\": [\"str\"], \"this_week\": [\"str\"]}}\n\nGap Analysis:\n{gap_analysis_json}"
        return self._run_agent_sync("placement-planner", prompt)

    def analyze_document(self, text, doc_type="resume"):
        import json
        if doc_type == "resume":
            return json.loads(self.analyze_resume(text))
        else:
            return json.loads(self.analyze_jd(text))

    def generate_analysis(self, prompt):
        return self._run_agent_sync("gap-analyzer", prompt)

