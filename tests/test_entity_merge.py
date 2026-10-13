def test_locales_remain_independent():
    row = {'en': 'Haste', 'fr': 'Hâte'}
    row.update({'de': 'Tempo'})
    assert row['fr'] == 'Hâte'
