import pytest

from tracked_dict.tracked_dict import TrackedDict


def test_getitem_tracks_access():
    d = TrackedDict(a=1, b=2)
    _ = d['a']
    assert 'a' in d.accessed_keys
    assert 'b' not in d.accessed_keys

def test_get_tracks_access():
    d = TrackedDict(a=1, b=2)
    _ = d.get('b')
    assert 'b' in d.accessed_keys
    assert 'a' not in d.accessed_keys

def test_get_with_default_tracks_access():
    # This confirms that the `TrackedDict.get()` method logs attempted accesses, even when the key isn't present
    # and a default is returned.
    d = TrackedDict(a=1)
    _ = d.get('missing', 42)
    assert 'missing' in d.accessed_keys

def test_assert_all_keys_accessed_passes():
    d = TrackedDict(x=10, y=20)
    _ = d['x']
    _ = d['y']
    d.assert_all_keys_accessed()

def test_assert_all_keys_accessed_fails():
    d = TrackedDict(p=1, q=2)
    _ = d['p']
    with pytest.raises(AssertionError):
        d.assert_all_keys_accessed()

def test_empty_dict_access_passes():
    d = TrackedDict()
    d.assert_all_keys_accessed()
