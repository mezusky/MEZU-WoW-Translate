"""Script-sensitive locale contracts must agree across audit and quality gates.

Synthetic browserCases test the gate only; they are not actual browser evidence.
"""
import unittest

from scripts.audit_locale_contract import resolve_audit_locale_contract
from scripts.quality_trend import summarize


def quality_fixture(source, target):
    pages = [
        ("warrior", "protection", "tank", "rotation-cooldowns-pve-tank", "rotation"),
        ("priest", "discipline", "healer", "talent-builds-pve-healer", "talents"),
        ("mage", "arcane", "dps", "bis-gear", "gear"),
        ("monk", "brewmaster", "tank", "mythic-plus-dungeon-tips", "mythic-plus"),
        ("evoker", "preservation", "healer", "midnight-season-2-raid-tips", "raid"),
    ]
    cases = [
        {
            "url": f"https://www.wowhead.com/guide/classes/{cls}/{spec}/{slug}",
            "wowClass": cls, "spec": spec, "role": role, "section": section,
            "sourceLanguage": source, "targetLanguage": target,
            "heldout": i < 2, "browserRendered": True, "strictPass": True,
        }
        for i, (cls, spec, role, slug, section) in enumerate(pages)
    ]
    return {"qualitySample": {
        "cycleId": "synthetic-script-contract",
        "auditedAt": "2026-10-31T18:00:00+01:00",
        "sourceLanguage": source, "targetLanguage": target,
        "newPagesAudited": len(cases), "novelIssueFamilies": 0,
        "browserVerifiedPages": len(cases), "browserCases": cases,
        "auditMethod": "browser-rendered", "crossRoleVerified": True,
        "unrelatedHeldoutsVerified": True, "strictAuditPassed": True,
    }}


class ScriptConversionAuditConsistencyTests(unittest.TestCase):
    def test_script_conversion_requires_explicit_pack_pair(self):
        for source, target in (("zh-CN", "zh-TW"), ("zh-Hans", "zh-Hant"),
                               ("sr-Cyrl", "sr-Latn")):
            with self.subTest(source=source, target=target):
                generic = {"sourceLanguage": source.split("-")[0],
                           "targetLanguage": target.split("-")[0]}
                self.assertEqual(
                    resolve_audit_locale_contract(
                        {"sourceLanguage": source, "targetLanguage": target}, generic
                    )["status"], "pack_locale_mismatch"
                )
                explicit = {"sourceLanguage": source, "targetLanguage": target}
                self.assertEqual(
                    resolve_audit_locale_contract(
                        {"sourceLanguage": source, "targetLanguage": target}, explicit
                    )["status"], "ready"
                )

    def test_script_alias_without_conversion_is_skipped(self):
        for source, target in (("zh-Hans", "zh-CN"), ("zh-Hant", "zh-TW"),
                               ("en-US", "en-GB"), ("sr-Cyrl", "sr-Cyrl")):
            with self.subTest(source=source, target=target):
                result = resolve_audit_locale_contract(
                    {"sourceLanguage": source, "targetLanguage": target},
                    {"sourceLanguage": source, "targetLanguage": target},
                )
                self.assertEqual(result["status"], "skipped_same_language")
                self.assertFalse(summarize([quality_fixture(source, target)])
                                 ["cycles"][0]["strictCleanCycle"])

    def test_quality_gate_recognizes_real_script_conversion_direction(self):
        for source, target in (("zh-CN", "zh-TW"), ("zh-TW", "zh-CN"),
                               ("zh-Hans", "zh-Hant"), ("sr-Cyrl", "sr-Latn"),
                               ("en-US", "fr-FR")):
            with self.subTest(source=source, target=target):
                result = summarize([quality_fixture(source, target)])
                self.assertTrue(result["cycles"][0]["strictCleanCycle"])
                # A single synthetic cycle never authorizes stopping.
                self.assertFalse(result["eligibleToConsiderStopping"])


if __name__ == "__main__":
    unittest.main()
