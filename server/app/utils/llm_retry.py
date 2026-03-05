"""
Retry helper for LLM invocations on 429 RESOURCE_EXHAUSTED.
"""

import re
import time


def invoke_with_retry(llm, messages, max_retries=2):
    """
    Invoke LLM with messages; on 429 RESOURCE_EXHAUSTED, wait and retry.
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            return llm.invoke(messages)
        except Exception as e:
            last_error = e
            err_str = str(e)
            if "429" in err_str and "RESOURCE_EXHAUSTED" in err_str and attempt < max_retries - 1:
                match = re.search(r"retry in (\d+(?:\.\d+)?)\s*s", err_str, re.I)
                wait = float(match.group(1)) if match else 15.0
                wait = min(wait, 60.0)
                time.sleep(wait)
                continue
            raise
    raise last_error
