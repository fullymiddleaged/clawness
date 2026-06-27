---
name: add
description: >
  Create a new Clawness rule from a natural language description.
  Describe what you want enforced and this will generate the YAML
  rule file with proper tags, triggers, and examples.
---

# Create a New Rule

Generate a Clawness rule from the user's description.

## Process

1. **Understand the intent** — The user describes a coding practice they
   want enforced. Parse their description for:
   - What domain this falls under (nextjs, react, python, etc.)
   - Whether it should be mandatory (always enforced) or ranked
   - The severity (error for "must do", warning for "should do", info for "consider")

2. **Generate the YAML** — Create a properly formatted rule:
   ```yaml
   id: DOMAIN-DESCRIPTIVE-NNN
   domain: detected_domain
   severity: error|warning|info
   tags: [relevant, search, keywords]
   triggers: [code, tokens, that, signal, relevance]
   when: Clear condition for when this rule applies.
   rule: >
     The actual instruction, written clearly and specifically.
   violation: "Concrete example of what NOT to do"
   correct: "Concrete example of what TO do"
   ```

3. **Tags and triggers are critical** — These drive retrieval. Include:
   - The concepts involved (e.g., "caching", "auth", "state")
   - The code tokens someone would use (e.g., "useEffect", "fetch", "router")
   - The framework/library names (e.g., "nextjs", "prisma", "zod")

4. **Save the rule** — Determine the right location:
   - If `.clawness/rules/` exists in the project, save there (project-scoped)
   - Otherwise, save to the global rules directory
   - Ask the user to confirm before writing

5. **Test it** — Run a test query to verify the rule would be retrieved
   for the kind of prompt it should match.

## Example

User says: "Always use server actions for form mutations in Next.js"

→ Generates a rule with:
- domain: nextjs
- tags: [server-actions, forms, mutations, use-server]
- triggers: [form, submit, action, mutation, create, update, delete]
- Saves to the appropriate rules directory
