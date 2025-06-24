# Contributing to SQL-Mongo Pipeline

Thank you for considering contributing to this project! Here are some guidelines to help you get started.

## Getting Started

1. **Fork the repository** and clone your fork locally.
2. **Install dependencies:**
   ```bash
   python -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```
3. **Install pre-commit hooks (optional but recommended):**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Coding Style
- Use [PEP8](https://www.python.org/dev/peps/pep-0008/) style.
- Add type hints to all functions.
- Write docstrings for all public functions and classes.
- Keep functions small and focused.

## Testing
- Write tests in `src/tests/` using `pytest`.
- Use the `mock_mongo_db` fixture for MongoDB-related tests.
- Run tests with:
  ```bash
  pytest src/tests/
  ```

## Making a Pull Request
1. Create a new branch: `git checkout -b feature/your-feature-name`.
2. Make your changes and add tests.
3. Update the `CHANGELOG.md` with your changes.
4. Push your branch and open a Pull Request (PR) on GitHub.
5. Ensure all tests pass and address any review comments.

## Code of Conduct
Please be respectful and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

---

Thank you for helping make this project better! 