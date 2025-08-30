# Test-Driven Development (TDD) Workflow

## Overview
This workflow guides you through implementing new features using Test-Driven Development methodology. Follow these 6 steps in order to ensure robust, well-tested code.

## When to Use This Workflow
- Adding new ESPN functionality to `gamedaybot/espn/functionality.py`
- Creating new chat platform integrations
- Implementing Discord commands
- Adding utility functions
- Creating scheduled jobs

## Prerequisites
- Python 3.7+ environment activated
- Dependencies installed: `pip install -r requirements.txt requirements-test.txt`
- Git repository initialized and configured
- Basic understanding of pytest testing framework

---

## Step 1: Clarify Requirements

### Goal
Define clear, testable requirements before writing any code.

### Actions
1. **Document the feature requirements**:
   - What problem does this feature solve?
   - What are the expected inputs and outputs?
   - What are the acceptance criteria?

2. **Identify dependencies**:
   - ESPN API endpoints needed
   - Chat platform integrations required
   - External services or data sources

3. **Define edge cases**:
   - Empty or invalid inputs
   - Network failures
   - API rate limits
   - Error conditions

4. **Create a requirements document**:
   ```markdown
   # Feature: [Feature Name]
   
   ## Description
   [Detailed description of what the feature should do]
   
   ## Acceptance Criteria
   - Given [initial condition]
   - When [action is performed]  
   - Then [expected result]
   
   ## Dependencies
   - [List APIs, modules, services needed]
   
   ## Edge Cases
   - [List potential failure scenarios]
   ```

### Example
For a "get_weekly_mvp" feature:
- **Purpose**: Find the highest scoring player for a given week
- **Input**: League object, optional week number
- **Output**: Formatted string with player name and score
- **Dependencies**: ESPN API league data, box scores
- **Edge Cases**: Invalid week, no games played, tied scores

---

## Step 2: Write Unit Tests, Run and Confirm Failures

### Goal
Write failing tests first (Red phase of TDD). Tests should fail because the feature doesn't exist yet.

### Actions
1. **Create test file** in `tests/` directory:
   ```bash
   touch tests/test_[feature_name].py
   ```

2. **Write comprehensive test cases**:
   ```python
   import pytest
   from unittest.mock import Mock, patch
   from gamedaybot.espn.functionality import [feature_name]
   
   class Test[FeatureName]:
       """Test suite for [feature_name] functionality"""
       
       def test_[feature_name]_basic_functionality(self):
           """Test basic [feature_name] functionality"""
           # Arrange
           mock_league = Mock()
           # Setup mock data based on requirements
           
           # Act
           result = [feature_name](mock_league)
           
           # Assert
           assert "expected content" in result
           
       def test_[feature_name]_edge_cases(self):
           """Test edge cases identified in requirements"""
           # Test invalid inputs, empty data, etc.
           pass
   ```

3. **Use existing patterns** from the project:
   - Mock ESPN League objects (see `tests/test_*.py` examples)
   - Use `requests_mock` for HTTP calls (see `tests/conftest.py`)
   - Follow naming conventions from existing tests

4. **Run tests and confirm they fail**:
   ```bash
   python -m pytest tests/test_[feature_name].py -v
   ```
   
   **Expected result**: All tests should fail (Red phase)

### Example Test Structure
```python
# tests/test_get_weekly_mvp.py
import pytest
from unittest.mock import Mock
from gamedaybot.espn.functionality import get_weekly_mvp

def test_get_weekly_mvp_returns_highest_scorer():
    """Test that MVP function returns the highest scoring player"""
    # This should fail initially since function doesn't exist
    mock_league = Mock()
    result = get_weekly_mvp(mock_league, week=5)
    assert "MVP:" in result
    assert "points" in result
```

---

## Step 3: Implement Feature

### Goal
Write the minimum code necessary to make tests pass (Green phase of TDD).

### Actions
1. **Determine target file**:
   - ESPN functionality → `gamedaybot/espn/functionality.py`
   - Chat integration → `gamedaybot/chat/[platform].py`
   - Utility function → `gamedaybot/utils/util.py`
   - Discord command → `gamedaybot/chat/discord_bot.py`

2. **Implement minimal function**:
   ```python
   def [feature_name](league, **kwargs):
       """
       [Feature description from requirements]
       
       Args:
           league: ESPN League object
           **kwargs: Additional arguments
           
       Returns:
           str: Formatted result
       """
       # Start with simplest implementation that passes tests
       pass
   ```

3. **Follow project patterns**:
   - Use existing error handling patterns
   - Follow docstring format from other functions
   - Use consistent variable naming
   - Handle edge cases identified in requirements

4. **Implement incrementally**:
   - Start with basic happy path
   - Add error handling
   - Handle edge cases
   - Optimize only if needed

### Implementation Guidelines
- **YAGNI Principle**: Don't implement features not covered by tests
- **Keep it simple**: Write minimal code to pass tests
- **Use existing utilities**: Leverage functions from `gamedaybot/utils/util.py`
- **Follow project style**: Match coding patterns from similar functions

---

## Step 4: Run Tests, Fix Bugs and Tests Until They Pass

### Goal
Iteratively run tests and fix issues until all tests pass (completing Green phase).

### Actions
1. **Run tests continuously**:
   ```bash
   python -m pytest tests/test_[feature_name].py -v --tb=short
   ```

2. **Analyze failures**:
   - Read error messages carefully
   - Check function signatures match test expectations
   - Verify return values meet test assertions
   - Ensure mock objects are configured correctly

3. **Fix implementation or tests**:
   - Fix bugs in implementation
   - Correct test expectations if requirements changed
   - Add missing error handling
   - Update mock configurations

4. **Run full test suite**:
   ```bash
   python -m pytest tests/ -x
   ```
   Ensure new feature doesn't break existing functionality.

5. **Check test coverage**:
   ```bash
   python -m pytest tests/test_[feature_name].py --cov=gamedaybot --cov-report=term-missing
   ```
   Aim for >80% coverage on new code.

### Debugging Common Issues
- **Import errors**: Check module paths and imports
- **Mock failures**: Verify mock object configuration matches usage
- **Assertion errors**: Compare expected vs actual values
- **TypeError**: Check function signatures and parameter types

---

## Step 5: Update Documentation

### Goal
Document the new feature for future developers and users.

### Actions
1. **Update function docstring**:
   ```python
   def [feature_name](league, **kwargs):
       """
       [Detailed description of what function does]
       
       This function implements [specific functionality] by [brief explanation].
       
       Args:
           league (espn_api.football.League): ESPN League object with team data
           week (int, optional): Week number (defaults to current week)
           
       Returns:
           str: Formatted string containing [description of output]
           
       Raises:
           ValueError: When [specific error condition]
           
       Example:
           >>> league = League(league_id=12345, year=2024)
           >>> result = [feature_name](league, week=5)
           >>> print(result)
           'Week 5 MVP: John Smith (Team A) - 156.8 points'
       """
   ```

2. **Update relevant documentation**:
   - Add function to appropriate `.clinerules/*.md` files
   - Update function lists in project documentation
   - Add usage examples where appropriate

3. **Register function** (if applicable):
   - Add to `gamedaybot/espn/espn_bot.py` for chat bot usage
   - Add to `gamedaybot/espn/scheduler.py` for scheduled execution
   - Add Discord command in `gamedaybot/chat/discord_bot.py`

4. **Document any new dependencies** or configuration requirements

### Documentation Checklist
- [ ] Function docstring with examples
- [ ] Updated relevant `.clinerules` documentation  
- [ ] Added to appropriate function registries
- [ ] Documented configuration requirements
- [ ] Added troubleshooting notes for common issues

---

## Step 6: Git Commit and Push

### Goal
Commit the completed feature with proper documentation for future reference.

### Actions
1. **Review changes**:
   ```bash
   git status
   git diff
   ```

2. **Stage all related files**:
   ```bash
   git add tests/test_[feature_name].py
   git add gamedaybot/[module]/[file].py
   git add .clinerules/*.md  # if documentation updated
   ```

3. **Create conventional commit**:
   ```bash
   git commit -m "[type]([scope]): add [feature_name] with TDD approach

   - Implemented [feature_name] following TDD methodology
   - Added comprehensive test suite with [X] test cases
   - Achieved [X]% test coverage
   - Updated documentation with usage examples
   - Integrated with existing [module] functionality

   Closes #[issue_number]"
   ```

4. **Push changes**:
   ```bash
   git push origin [branch_name]
   ```

### Commit Types
- `feat`: New feature implementation
- `fix`: Bug fix  
- `docs`: Documentation updates only
- `test`: Adding or updating tests
- `refactor`: Code changes without functional changes

### Example Commit
```bash
git commit -m "feat(espn): add get_weekly_mvp with TDD approach

- Implemented get_weekly_mvp following TDD methodology
- Added comprehensive test suite with 5 test cases  
- Achieved 95% test coverage
- Updated functionality documentation with usage examples
- Integrated with existing ESPN bot functionality

Closes #123"
```

---

## TDD Workflow Validation Checklist

Before considering the workflow complete, verify:

### Requirements (Step 1)
- [ ] Clear feature requirements documented
- [ ] Acceptance criteria defined in Given/When/Then format
- [ ] Dependencies and edge cases identified
- [ ] Requirements review completed

### Tests (Step 2)
- [ ] Comprehensive test suite created
- [ ] Tests initially failed (Red phase confirmed)
- [ ] Edge cases covered in tests
- [ ] Mock objects properly configured

### Implementation (Step 3)
- [ ] Minimal code written to pass tests
- [ ] Followed existing project patterns
- [ ] Error handling implemented
- [ ] Function signature matches test expectations

### Validation (Step 4)  
- [ ] All new tests pass (Green phase achieved)
- [ ] Full test suite passes (no regressions)
- [ ] Test coverage >80% on new code
- [ ] No linting errors or warnings

### Documentation (Step 5)
- [ ] Function docstring with examples
- [ ] Relevant project documentation updated
- [ ] Function registered in appropriate modules
- [ ] Configuration requirements documented

### Git (Step 6)
- [ ] Changes committed with conventional format
- [ ] Descriptive commit message with details
- [ ] All related files included in commit
- [ ] Changes pushed to remote repository

## Refactoring Phase (Optional)

After completing the Red-Green cycle, you may refactor:

1. **Improve code quality** without changing functionality
2. **Extract common patterns** into utility functions  
3. **Optimize performance** if needed
4. **Update tests** to reflect refactored code
5. **Ensure all tests still pass** after refactoring

Remember: Never refactor without tests in place!

---

## Common TDD Anti-Patterns to Avoid

- **Writing implementation before tests** - Always write failing tests first
- **Testing implementation details** - Test behavior, not internal structure
- **Skipping edge cases** - Test failure scenarios and boundary conditions  
- **Large test/code cycles** - Keep changes small and incremental
- **Not running tests frequently** - Run tests after every small change
- **Ignoring test failures** - Fix failing tests immediately

## Resources

- [Project Testing Guide](../.clinerules/testing.md)
- [Development Guide](../.clinerules/development-guide.md) 
- [Existing test examples](../../tests/)
- [ESPN API Documentation](https://github.com/cwendt94/espn-api)