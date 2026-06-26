---
name: test
description: >
  Generate comprehensive tests for a file or module. Reads existing
  test patterns and matches the project's style. Covers happy paths,
  edge cases, error conditions, and boundary values.
---

# Test Generation

Generate tests using the Clawness test-writer agent.

## Steps

1. **Target** — If $ARGUMENTS specifies a file or function, test that.
   Otherwise, find recently changed files without corresponding tests.

2. **Delegate to test-writer** — Send the target code to the
   `test-writer` sub-agent. It will:
   - Read existing tests to match the project's style
   - Plan test cases covering happy path, edge cases, errors, boundaries
   - Write the test file(s)
   - Run them and fix any test-level issues

3. **Report** — Show what was tested, any bugs discovered by the tests,
   and the test file location.
