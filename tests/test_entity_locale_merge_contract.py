def test_locale_data_shape():
    row = {'en': 'Frost Strike', 'fr': 'Frappe de givre'}
    assert row['en'] and row['fr']
