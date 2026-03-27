class TrackedDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.accessed_keys = set()

    def __getitem__(self, key):
        self.accessed_keys.add(key)
        return super().__getitem__(key)

    def get(self, key, default=None, /):
        self.accessed_keys.add(key)
        return super().get(key, default)

    def assert_all_keys_accessed(self):
        all_keys = set(self.keys())
        missing = all_keys - self.accessed_keys
        # Sort the output for readability
        assert not missing, f"Unaccessed keys: {', '.join(repr(k) for k in sorted(missing))}"
