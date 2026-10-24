import unittest
from scripts.html_block_extractor import extract_blocks, extract_readable_blocks


class TestExtractor(unittest.TestCase):
    def test_nested_list(self):
        blocks = extract_blocks('<li>Before <p>Inside</p> After</li>')
        self.assertIn(('li', 'Before Inside After'), blocks)

    def test_script_is_ignored(self):
        self.assertEqual(extract_blocks('<p>Before<script>BAD</script>After</p>'), [('p', 'Before After')])

    def test_article_scope_excludes_site_navigation(self):
        html = ('<nav><p>Old outdated guide from navigation.</p></nav>'
                '<main><h1>Raid Tips</h1><p>Use your cooldowns.</p>'
                '<p>React to procs.</p><li>Keep casting.</li></main>'
                '<footer><p>Footer content.</p></footer>')
        self.assertEqual(extract_readable_blocks(html),
                         [('h1', 'Raid Tips'), ('p', 'Use your cooldowns.'),
                          ('p', 'React to procs.'), ('li', 'Keep casting.')])

    def test_unscoped_fallback_for_pages_without_main_or_article(self):
        html = '<h1>Guide</h1><p>One</p><p>Two</p><p>Three</p>'
        self.assertEqual(extract_readable_blocks(html), extract_blocks(html))

    def test_article_scope_excludes_hidden_widgets(self):
        html = ('<main><h1>Talents</h1><div hidden><p>Obsolete build</p></div>'
                '<p>Visible priority</p><p>Raid strategy</p><p>Gear choices</p></main>')
        self.assertEqual(extract_readable_blocks(html),
                         [('h1', 'Talents'), ('p', 'Visible priority'),
                          ('p', 'Raid strategy'), ('p', 'Gear choices')])
