"""WoW macro commands must not pollute source-language audits.

Source examples: Arcane Mage, Protection Paladin, Discipline Priest, and
Outlaw Rogue UI/Macros guides (Midnight). This does not test Chrome DOM output.
"""
import unittest

from scripts.source_language_evidence import clean_non_prose


class MacroAuditTests(unittest.TestCase):
    def test_tank_macro_preserves_surrounding_explanation(self):
        text = (
            "Use this macro to cast a defensive spell on yourself.\n"
            "    #showtooltip Divine Shield\n"
            "    /stopcasting\n"
            "    /cancelaura Divine Shield\n"
            "    /cast Divine Shield\n"
            "This can be used to both cast and cancel Divine Shield."
        )
        cleaned = clean_non_prose(text)
        self.assertIn("Use this macro to cast", cleaned)
        self.assertIn("This can be used", cleaned)
        for command in ("#showtooltip", "/stopcasting", "/cancelaura", "/cast Divine"):
            self.assertNotIn(command, cleaned)

    def test_healer_macro_with_conditionals_and_targeting(self):
        text = (
            "Mouseover macros help with healing.\n"
            "#showtooltip Flash Heal\n"
            "/cast [@mouseover,help,nodead][] Flash Heal\n"
            "/target Object Name\n"
            "/focus\n"
            "/targetlasttarget\n"
            "The target selection remains useful."
        )
        cleaned = clean_non_prose(text)
        self.assertIn("Mouseover macros help", cleaned)
        self.assertIn("The target selection remains useful.", cleaned)
        self.assertNotIn("[@mouseover", cleaned)
        self.assertNotIn("/target", cleaned)

    def test_dps_macro_castsequence_and_use(self):
        text = (
            "#showtooltip Touch of the Magi\n"
            "/use 13\n"
            "/castsequence reset=10 Arcane Barrage, Touch of the Magi\n"
            "/cqs\n"
            "Use your trinkets together with major cooldowns."
        )
        cleaned = clean_non_prose(text)
        self.assertEqual(cleaned.strip(), "Use your trinkets together with major cooldowns.")

    def test_inline_commands_and_unrelated_paths_are_not_hidden(self):
        text = (
            "Type /cast in the macro window and use /focus for your target.\n"
            "The /guide/classes/ path is a URL path, not a macro.\n"
            "/customcommand is not in the conservative allowlist."
        )
        self.assertEqual(clean_non_prose(text), text)


if __name__ == "__main__":
    unittest.main()
