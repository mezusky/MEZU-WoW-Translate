"""Cross-guide executable macro invariants for captured translations."""
import unittest

from scripts.audit_translation_samples import audit_sample


class ProtectedCommandsTests(unittest.TestCase):
    def audit(self, source, translated, source_language="en", target_language="fr"):
        return audit_sample({
            "sourceLanguage": source_language,
            "targetLanguage": target_language,
            "source": source,
            "translated": translated,
        })

    def test_discipline_console_command_preserved(self):
        source = "Stop camera movement:\n/console cameraSmoothTrackingStyle 0"
        target = "Désactiver le mouvement de caméra :\n/console cameraSmoothTrackingStyle 0"
        self.assertNotIn("protected_command_mismatch", self.audit(source, target))

    def test_discipline_console_command_changed(self):
        source = "Stop camera movement:\n/console cameraSmoothTrackingStyle 0"
        target = "Désactiver le mouvement de caméra :\n/console cameraSmoothTrackingStyle 1"
        self.assertIn("protected_command_mismatch", self.audit(source, target))

    def test_lua_macro_not_translated(self):
        source = "Macro:\n/run print(GetLocale())\n/script print(1)"
        target = "Macro :\n/run print(GetLocale())\n/script afficher(1)"
        self.assertIn("protected_command_mismatch", self.audit(source, target))

    def test_cast_spell_localization_is_allowed(self):
        source = "Macro:\n/cast Smite"
        target = "Macro :\n/cast Châtiment"
        self.assertNotIn("protected_command_mismatch", self.audit(source, target))

    def test_command_checks_are_target_locale_independent(self):
        source = "/console cameraSmoothTrackingStyle 0"
        target = "/console cameraSmoothTrackingStyle 1"
        self.assertIn("protected_command_mismatch", self.audit(source, target, "en-US", "de-DE"))


if __name__ == "__main__":
    unittest.main()
