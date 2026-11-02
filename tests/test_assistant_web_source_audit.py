"""Direct assistant web source audits remain source-only, never Chrome evidence."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.source_intervention_trend import load_cycles, summarize


class AssistantWebSourceAuditTests(unittest.TestCase):
    def test_live_source_is_counted_but_never_browser_verified(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            audits = root / "audits"
            audits.mkdir()
            history = root / "history.json"
            corpus = root / "corpus.json"
            history.write_text('{"cycles":[]}', encoding="utf-8")
            corpus.write_text(json.dumps({"pages": [
                {"id": "tank"}, {"id": "healer"}, {"id": "dps"}
            ]}), encoding="utf-8")
            report = {
                "date": "2026-11-02",
                "auditMethod": "assistant-web-source-only",
                "sourceInterventionSample": {
                    "cycleId": "direct-source-three-roles",
                    "sourceLanguage": "en", "targetLanguage": "fr",
                    "sampledPageIds": ["tank", "healer", "dps"],
                    "sampledPageCount": 3,
                    "newReusableTermFamiliesObserved": 0,
                    "newManualSentenceOverrides": 0,
                    "browserRenderedPagesVerified": 0,
                },
            }
            path = audits / "sample.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            cycles = load_cycles(history, audits, corpus)
            self.assertEqual(len(cycles), 1)
            summary = summarize(cycles, window=1)
            self.assertEqual(summary["eligibleCycles"], 1)
            self.assertEqual(summary["recent"]["sampledPages"], 3)
            self.assertIsNone(summary["browserTranslationErrorRate"])

            report["sourceInterventionSample"]["browserRenderedPagesVerified"] = 1
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_cycles(history, audits, corpus)

            report["sourceInterventionSample"]["browserRenderedPagesVerified"] = 0
            report["auditMethod"] = "browser-verified"
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_cycles(history, audits, corpus)


if __name__ == "__main__":
    unittest.main()
