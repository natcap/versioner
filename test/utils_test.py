import unittest


class TagIncrementTest(unittest.TestCase):
    def test_three_digit_version(self):
        """Versioner - Utils: verify three-part version increments."""
        from natcap.versioner import versioning
        version = '0.0.1'
        self.assertEqual(versioning._increment_tag(version), '0.0.2')

    def test_two_digit_version(self):
        """Versioner - Utils: verify two-part version increments."""
        from natcap.versioner import versioning
        version = '0.1'
        self.assertEqual(versioning._increment_tag(version), '0.2')

    def test_one_digit_version(self):
        """Versioner - Utils: verify one-part version increments."""
        from natcap.versioner import versioning
        version = '1'
        self.assertEqual(versioning._increment_tag(version), '2')
