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


    def test_rogue_focus_and_sap_targeting_lines(self):
        # Subtlety Rogue UI/Macros, independent of the original Mage sample.
        text = (
            "You can set a focus target with the following macro:\n"
            "/focus\n"
            "A spammable Sap macro is useful in PvP.\n"
            "#showtooltip Sap\n"
            "/cleartarget\n"
            "/targetenemyplayer\n"
            "/cast Sap\n"
            "Keep your focus target for interrupts."
        )
        cleaned = clean_non_prose(text)
        self.assertIn("You can set a focus target", cleaned)
        self.assertIn("A spammable Sap macro", cleaned)
        self.assertIn("Keep your focus target", cleaned)
        for command in ("/focus", "/cleartarget", "/targetenemyplayer", "#showtooltip"):
            self.assertNotIn(command, cleaned)

    def test_hunter_pet_and_targeting_commands(self):
        # Marksmanship Hunter UI/Macros: a different class and role.
        text = (
            "Use this macro to manage your pet and focus.\n"
            "/petpassive\n"
            "/petfollow\n"
            "/petattack\n"
            "/stopmacro [noexists]\n"
            "/tm 4\n"
            "/targetenemy\n"
            "/clearfocus\n"
            "/startattack\n"
            "The explanatory paragraph remains."
        )
        cleaned = clean_non_prose(text)
        self.assertEqual(
            " ".join(cleaned.split()),
            "Use this macro to manage your pet and focus. The explanatory paragraph remains."
        )
        # Inline documentation remains prose, not an executable macro line.
        self.assertEqual(
            clean_non_prose("Type /focus or /cleartarget in the macro window."),
            "Type /focus or /cleartarget in the macro window."
        )


    def test_arcane_console_command_is_not_a_translation_candidate(self):
        # Arcane and Fire Mage rotation guides document SpellQueueWindow.
        text = (
            "Use the default spell queue window for smooth casts.\n"
            "/console SpellQueueWindow 400\n"
            "Continue casting spells without downtime."
        )
        cleaned = clean_non_prose(text)
        self.assertNotIn("/console SpellQueueWindow", cleaned)
        self.assertIn("default spell queue window", cleaned)
        self.assertIn("Continue casting spells", cleaned)
        # Mentions in prose are not whole executable lines.
        inline = "Type /console SpellQueueWindow 400 in the chat window."
        self.assertEqual(clean_non_prose(inline), inline)
        self.assertEqual(clean_non_prose("/consoleexample is not a command."), "/consoleexample is not a command.")


    def test_run_click_and_tar_are_executable_not_guide_prose(self):
        # Indexed Shadow Priest (PI macro), Evoker (Rescue) and Warlock
        # macro guides contain these commands; their Lua must not be learned.
        examples = (
            ("Shadow Priest", '/run local n=UnitName("target") or "player"'),
            ("Affliction Warlock", "/click StaticPopup1Button1"),
            ("Augmentation Evoker", "/tar [@focus]"),
            ("Warlock script alias", "/script SetRaidTarget('target', 1)"),
            ("Tooltip directive", "#show Power Infusion"),
        )
        for guide, command in examples:
            with self.subTest(guide=guide):
                source = "Explain the macro before use.\n" + command + (
                    "\nThe next paragraph is ordinary English guide prose."
                )
                cleaned = clean_non_prose(source)
                self.assertNotIn(command, cleaned)
                self.assertIn("Explain the macro before use.", cleaned)
                self.assertIn("The next paragraph is ordinary English", cleaned)

    def test_inline_macro_documentation_and_prefixes_remain_visible(self):
        # A command mention inside prose is not an executable directive.
        text = (
            "Type /run or /click in the macro editor.\n"
            "Use /tar to select a focus target.\n"
            "/runner is not a supported macro directive.\n"
            "/clickable is not a supported macro directive."
        )
        self.assertEqual(clean_non_prose(text), text)



if __name__ == "__main__":
    unittest.main()
