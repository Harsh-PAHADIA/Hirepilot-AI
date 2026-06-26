import sys
from services.lemma_provider import LemmaProvider

provider = LemmaProvider()
print("Sending test request to jd-analyst...")
jd_text = "Looking for a React developer with Python."
res = provider.client.analyze_jd(jd_text)
print(f"Raw response: {res}")
print(f"Parsed response: {provider.analyze_jd(jd_text)}")

