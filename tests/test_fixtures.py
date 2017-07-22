

def test_fake_hash(fake_hash):
    assert fake_hash('rainstorms', encoding='bytes') == b"HASH(brainstorms)"
