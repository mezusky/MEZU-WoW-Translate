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
