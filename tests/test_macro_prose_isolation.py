"""Source-only WoW macro-guide audits must exclude non-prose payloads.

Synthetic markup models independent indexed Wowhead UI/Macros guides for
Protection Warrior, Preservation Evoker, Fire Mage and Protection Paladin.
These tests do NOT validate the Chrome extension or browser Translator API.
"""
import unittest

from scripts.html_block_extractor import extract_readable_blocks


class MacroProseIsolationTests(unittest.TestCase):
    def test_tank_macro_payload_and_copy_button_are_not_prose(self):
        html = (
            '<main><h2>Protection Warrior Macros</h2>'
            '<p>Use your trinket with Avatar.</p>'
            '<pre><code>#showtooltip Avatar\n/use 13\n/cast Avatar</code></pre>'
            '<button type="button">Copy Macro</button>'
            '<p>Replace the sample spell with your own ability.</p></main>'
        )
        self.assertEqual(extract_readable_blocks(html), [
            ('h2', 'Protection Warrior Macros'),
            ('p', 'Use your trinket with Avatar.'),
            ('p', 'Replace the sample spell with your own ability.'),
        ])

    def test_healer_inline_code_preserves_surrounding_explanation(self):
        html = (
            '<article><h2>Preservation Evoker Macros</h2>'
            '<p>Use <code>/cast [@mouseover] Sample Spell</code> '
            'to heal allies without changing target.</p>'
            '<p>Rescue can be used with a mouseover macro.</p></article>'
        )
        self.assertEqual(extract_readable_blocks(html), [
            ('h2', 'Preservation Evoker Macros'),
            ('p', 'Use to heal allies without changing target.'),
            ('p', 'Rescue can be used with a mouseover macro.'),
        ])

    def test_caster_item_ids_and_import_text_are_not_prose(self):
        html = (
            '<main><h2>Fire Mage UI</h2>'
            '<p>Use item IDs to activate your trinket.</p>'
            '<pre>/use item:245898\n/cast Combustion</pre>'
            '<textarea>1|ABC+/opaqueimport</textarea>'
            '<p>Focus and mouseover macros can interrupt enemies.</p></main>'
        )
        self.assertEqual(extract_readable_blocks(html), [
            ('h2', 'Fire Mage UI'),
            ('p', 'Use item IDs to activate your trinket.'),
            ('p', 'Focus and mouseover macros can interrupt enemies.'),
        ])

    def test_unrelated_tank_preserves_spell_links_and_table_prose(self):
        html = (
            '<main><h2>Protection Paladin</h2>'
            '<table><tr><td>Use <a href="/spell=642">Divine Shield</a> '
            'for emergencies.</td><td><button>Copy UI</button></td></tr></table>'
            '<p>Cancel an unwanted buff with a macro.</p></main>'
        )
        self.assertEqual(extract_readable_blocks(html), [
            ('h2', 'Protection Paladin'),
            ('td', 'Use Divine Shield for emergencies.'),
            ('p', 'Cancel an unwanted buff with a macro.'),
        ])

    def test_nested_code_and_markup_do_not_hide_following_prose(self):
        html = (
            '<article><p>Before <pre><code><span>/cast Spell</span>'
            '</code></pre> after the macro.</p>'
            '<p>Other useful recommendations remain visible.</p></article>'
        )
        self.assertEqual(extract_readable_blocks(html), [
            ('p', 'Before after the macro.'),
            ('p', 'Other useful recommendations remain visible.'),
        ])


if __name__ == "__main__":
    unittest.main()
