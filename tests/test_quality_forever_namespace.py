"""Forever guide URLs are real cross-version audit identities, not retail aliases.

Source-only indexed pages establish these URL shapes. These tests do not
claim that Chrome's translated output has been inspected.
"""
import unittest

from scripts.quality_trend import _canonical_guide_url, _case_matches_guide_identity


BASE = "https://www.wowhead.com"
GUIDES = (
    ("warrior", "protection", "tank"),
    ("priest", "discipline", "healer"),
    ("mage", "frost", "dps"),
)


class ForeverQualityIdentityTests(unittest.TestCase):
    def test_three_independent_forever_roles_are_eligible_for_future_browser_audits(self):
        for wow_class, spec, role in GUIDES:
            with self.subTest(spec=spec):
                url = (f"{BASE}/forever/guide/classes/{wow_class}/{spec}/"
                       f"rotation-cooldowns-pve-{role}")
                case = {"wowClass": wow_class, "spec": spec,
                        "role": role, "section": "rotation"}
                self.assertTrue(_case_matches_guide_identity(
                    case, _canonical_guide_url(url)))

    def test_localized_forever_variants_are_not_independent_pages(self):
        canonical = (f"{BASE}/forever/guide/classes/warrior/protection/"
                     "rotation-cooldowns-pve-tank")
        for locale in ("fr", "de", "en-US", "zh-TW"):
            with self.subTest(locale=locale):
                variant = canonical.replace("/forever/guide/",
                                            f"/forever/{locale}/guide/")
                self.assertEqual(_canonical_guide_url(variant + "?ref=nav#top"),
                                 canonical)

    def test_retail_and_forever_remain_independent_sources(self):
        retail = (f"{BASE}/guide/classes/warrior/protection/"
                  "rotation-cooldowns-pve-tank")
        forever = retail.replace("/guide/", "/forever/guide/")
        self.assertNotEqual(_canonical_guide_url(retail),
                            _canonical_guide_url(forever))

    def test_bad_forever_metadata_cannot_claim_strict_quality(self):
        url = (f"{BASE}/forever/guide/classes/priest/discipline/"
               "rotation-cooldowns-pve-healer")
        canonical = _canonical_guide_url(url)
        valid = {"wowClass": "priest", "spec": "discipline",
                 "role": "healer", "section": "rotation"}
        self.assertTrue(_case_matches_guide_identity(valid, canonical))
        for key, value in (("role", "dps"), ("spec", "holy"),
                           ("section", "talents")):
            with self.subTest(key=key):
                bad = dict(valid, **{key: value})
                self.assertFalse(_case_matches_guide_identity(bad, canonical))

    def test_forever_combat_rogue_has_a_product_scoped_role(self):
        # Live Forever Combat Rogue rotation (2026-10-30) is a DPS guide;
        # Retail uses Outlaw and must not inherit the legacy Combat alias.
        suffix = "/guide/classes/rogue/combat/rotation-cooldowns-pve-dps"
        case = {"wowClass": "rogue", "spec": "combat",
                "role": "dps", "section": "rotation"}
        self.assertTrue(_case_matches_guide_identity(
            case, _canonical_guide_url(BASE + "/forever" + suffix)))
        self.assertTrue(_case_matches_guide_identity(
            case, _canonical_guide_url(BASE + "/forever/fr" + suffix)))
        for namespace in ("", "/ptr", "/ptr-2"):
            with self.subTest(namespace=namespace):
                self.assertFalse(_case_matches_guide_identity(
                    case, _canonical_guide_url(BASE + namespace + suffix)))
        self.assertFalse(_case_matches_guide_identity(
            dict(case, role="tank"),
            _canonical_guide_url(BASE + "/forever" + suffix)))
        self.assertFalse(_case_matches_guide_identity(
            dict(case, section="talents"),
            _canonical_guide_url(BASE + "/forever" + suffix)))

    def test_new_forever_heldouts_cover_rotation_and_stats(self):
        import json
        from pathlib import Path

        corpus = (Path(__file__).resolve().parents[1] / "data" /
                  "wowhead_regression_pages.json")
        pages = json.loads(corpus.read_text(encoding="utf-8"))["pages"]
        urls = {page["url"] for page in pages}
        cases = (
            ("mage", "fire", "dps", "rotation-cooldowns-pve-dps", "rotation"),
            ("priest", "holy", "healer", "rotation-cooldowns-pve-healer", "rotation"),
            ("rogue", "combat", "dps", "rotation-cooldowns-pve-dps", "rotation"),
            ("mage", "fire", "dps", "stat-priority-pve-dps", "stats"),
        )
        for wow_class, spec, role, slug, section in cases:
            with self.subTest(spec=spec, section=section):
                url = f"{BASE}/forever/guide/classes/{wow_class}/{spec}/{slug}"
                self.assertIn(url, urls)
                case = {"wowClass": wow_class, "spec": spec,
                        "role": role, "section": section}
                self.assertTrue(_case_matches_guide_identity(
                    case, _canonical_guide_url(url)))

    def test_arbitrary_namespaces_and_invented_slugs_remain_rejected(self):
        case = {"wowClass": "warrior", "spec": "protection",
                "role": "tank", "section": "rotation"}
        for path in (
            "/forever-preview/guide/classes/warrior/protection/rotation-cooldowns-pve-tank",
            "/forever/guide/classes/warrior/protection/rotation-cooldowns-pve-tank-draft",
        ):
            with self.subTest(path=path):
                self.assertFalse(_case_matches_guide_identity(
                    case, _canonical_guide_url(BASE + path)))


if __name__ == "__main__":
    unittest.main()
