# Test Fixtures

This directory contains test fixtures and sample data for the Audiobook Creator TTS test suite.

## Contents

### Sample Documents

- **sample_test.txt**: Basic text file for testing TXT extraction and processing
- **voices_test.json**: Minimal voice configuration for testing voice management functions

### Audio Samples

Audio samples are generated during tests and not committed to the repository.

## Usage

Fixtures are automatically loaded by pytest via the conftest.py configuration. They can be used in tests through fixture injection:

```python
def test_something(fixtures_dir):
    sample_file = fixtures_dir / "sample_test.txt"
    # Use sample file in test
```

## Adding New Fixtures

To add new test fixtures:

1. Create the file in this directory
2. Add a corresponding pytest fixture in `tests/conftest.py` if needed
3. Document the fixture purpose in this README

## Notes

- Keep fixtures small and focused on specific test scenarios
- Use realistic data that represents actual use cases
- Avoid including copyrighted or sensitive content
- Binary fixtures (PDF, EPUB) should be minimal and public domain
