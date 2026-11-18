---
name: bdd-gherkin
description: "Create and review BDD scenarios, Gherkin feature files (.feature), acceptance examples and their step definitions using the language of the problem domain - Given/When/Then, Rule, Scenario Outline, Background, Examples. Use when specifying expected behavior, turning a requirement or existing test into scenarios, or improving existing scenarios; routine test automation work alone does not require this skill."
---

# BDD and Gherkin

Write examples that help domain stakeholders agree on expected behavior and recognize the correct outcome. Gherkin records that agreement; it cannot supply missing requirements. Scenarios are specifications of behavior, not test scripts with BDD keywords on top. Apply this guidance across projects, domains, and automation frameworks.

## Choose the scenario language

Default to **English** for feature descriptions, rule and scenario titles, step text, and example-table headings. The language of the conversation alone does not change this default.

Resolve language choices in this order, following the normal precedence of instructions:

1. An explicit language request for the current task.
2. Applicable project instructions, such as `AGENT.md`, `AGENTS.md`, or `CLAUDE.md`, including lowercase equivalents such as `agent.md` and `claude.md`.
3. The established language of existing scenarios in the target feature or relevant suite, when instructions do not specify a language.
4. English when no applicable convention exists.

Follow the most relevant local convention rather than an unrelated example elsewhere in the repository. In a multilingual suite, preserve the language of the feature being edited. If an unresolved conflict affects the requested work, ask a focused question.

Treat natural-language text and Gherkin keyword dialect as separate choices. English keywords may accompany non-English step text. Preserve an existing keyword dialect; when using localized keywords, include the appropriate `# language:` header and take the keywords from the official list (`cucumber/gherkin`, `gherkin-languages.json`), not from memory. Keep domain terms, identifiers, and exact product messages unchanged when translation would alter their meaning.

## Learn the project's conventions and vocabulary

- Read project instructions and existing `.feature` files first. Follow their folder layout, file naming, actor names, step wording, and tags. Reuse existing steps before writing new ones.
- Take domain vocabulary from `GLOSSARY.md` (Matt Pocock's domain glossary) or another glossary when present, then from domain types and UI copy. Use those exact names; do not invent synonyms.
- Name feature files by capability in kebab-case, such as `order-checkout.feature`, unless the project uses another convention. Avoid names like `test1.feature` or `scenarios.feature`.

## Clarify rules without unnecessary questions

- Start with the task, existing specifications, and the project's domain vocabulary. Implementation can explain current behavior, but does not by itself establish intended behavior.
- Distinguish confirmed rules, concrete examples, and open questions. Do not infer an unspecified rate, permission, or time boundary merely to complete an example.
- Proceed when the available information is sufficient. Ask only about missing decisions that affect expected behavior. Group related questions and continue with independent cases that are already clear.
- If an outcome is unknown, record a question separately. Do not present guesses or placeholder `Then` steps as finished acceptance scenarios. Clearly label invented teaching examples as illustrative.
- For new behavior, use examples to clarify requirements before implementation. When reviewing existing tests, respect the review scope; translating tests into Gherkin after implementation does not by itself establish BDD.

## Formulate a focused example

- Name each `Feature` after a capability and each scenario after its distinguishing case or outcome, such as "A blocked date cannot be booked", not "Successful test" or "Booking 2". Use `Rule` when it helps group examples of one rule. Add a business-value statement when useful; an "As a / I want / So that" template is optional.
- Use domain vocabulary and consistent actor names. Write in the third person and present tense ("the customer adds"), unless the project already uses another point of view. Express the same concept consistently instead of introducing synonymous steps without a reason.
- `Given` establishes relevant starting conditions as state, not as a procedure. For example, "the administrator is signed in" need not describe the sign-in form. A `Given` never performs the action under test.
- `When` expresses an event or actor's intent at business level. Prefer one focused trigger; if a scenario needs a second unrelated trigger, split it. Allow related actions when their sequence is the behavior being specified. Use complete user journeys when they fit the task and purpose of the test.
- `Then` states a precise outcome observable by a user or collaborating system. Several related assertions may describe one behavior. Avoid vague success statements and internal database fields, HTTP status codes, or CSS classes as substitutes for observable results.
- `And` and `But` continue the previous step type. Each step says one thing; do not chain several actions with "and" inside one step. Do not use "or" in a step; express alternative inputs as separate examples.
- Apply the wording test: would this step change if the interface changed but the rule did not? If so, it is too low-level. Put selectors, URLs, incidental clicks, waits, SQL, and internal calls in step implementations. Retain a technical detail when it is part of the specified contract, such as a public API response or keyboard interaction.
- Keep inputs and expectations that explain the rule visible. Relevant amounts, quantities, roles, dates, and boundaries belong in the example. Parameters may naturally appear in `When`, such as "the customer pays $40". Move incidental data, such as names, phone numbers, or IDs, into step implementations.
- Prefer relative dates ("a date four months ahead") over fixed calendar dates that go stale, unless the rule concerns a specific date.
- Aim for roughly 3–5 steps as a readability guideline, not a limit. Much longer scenarios usually hide a second behavior or leaked detail. Do not hide unrelated behaviors inside one long step merely to reduce the count.

## Choose structure for readability

| Construct | Use it for |
| --- | --- |
| `Scenario` | One concrete example that is understandable on its own. |
| `Rule` | Examples of one business rule. A `Rule` can have its own `Background`. |
| `Scenario Outline` + `Examples` | The same behavior and expectation structure with meaningful data variations. Each row supplies another example, such as a case below, at, or above a boundary. |
| Data Table | Readable structured data for one step, including expected results. Field count alone does not justify a table. |
| `Background` | Short starting context shared by all scenarios in its `Feature` or `Rule`, about four lines at most. Keep the condition that distinguishes a specific example visible in that example. When scenarios need different setups, split them into another `Rule` or feature. |
| Doc String | Multiline content essential to the example. |
| Tags | Useful filtering, traceability, or established team workflows. Follow project conventions; do not add tags such as `@smoke` or `@regression` by reflex. |

Do not combine different stories into one parameterized template with switches and conditional steps. Choose representative cases and relevant boundaries rather than enumerating combinations that add no explanatory value. A large examples table usually hides several behaviors.

Each scenario must work independently without relying on an earlier scenario's results. Use controlled test data; realistic examples do not imply dependencies on existing production records. Shared context definitions in `Background` do not imply shared mutable state between runs.

## Write step definitions when automating

Apply this section only when the task includes automation.

- Keep selectors, URLs, navigation, waits, test data, and cleanup in step code only.
- Organize step files by domain concept, such as `orders.steps.ts` or `payments.steps.ts`, not one file per feature. Steps must be reusable across features.
- Use one wording for one meaning. Search for an existing step before adding a near-duplicate.
- Do not hand-edit generated test files, such as `playwright-bdd` output. Change the feature or the step definitions instead.
- Specify a rule that needs no interface or integration, such as a pure calculation, validation, or date arithmetic, in a unit test rather than in Gherkin.

## Create, review, and deliver

When creating scenarios, cover the supplied rules and meaningful distinctions: ordinary behavior, rejection, or boundaries where those rules are known. Do not mechanically generate the same categories for every capability.

When reviewing, identify the concrete problem and its effect on understanding, propose a rewrite, and preserve the original business meaning. Separate unclear or contradictory requirements from wording improvements.

Before delivering, check:

- Does the scenario language follow the language-selection rules above?
- Can a domain stakeholder understand the example without knowing the implementation?
- Are the project's domain terms and actor names used consistently?
- Are all necessary preconditions and precise, observable expectations present?
- Is each scenario focused on one behavior, with a related sequence of actions only where the sequence is the behavior?
- Are selectors, URLs, CSS classes, SQL, HTTP codes, and field-by-field typing kept out, except where they are the specified contract?
- Do outcomes, calculations, and boundaries follow explicitly established rules?
- Does each scenario name state its distinguishing case, and does each examples row contribute a useful distinction?
- Is `Background` short and free of conditions that distinguish individual examples?
- Can every scenario run independently and in any order?
- Does the rewrite preserve the request, with open questions listed separately?

Deliver the requested scenarios or review. Create files according to the task and project conventions. Writing Gherkin does not itself authorize framework installation or automation implementation. Claims that scenarios execute or pass require an actual run with matching step definitions; syntax validation establishes syntax only.

## Examples and sources

Read [references/examples.md](references/examples.md) when a concrete rewrite, data variation, background, language choice, or ambiguity example would help. Do not transfer its illustrative rules into the user's domain.

Use these sources to resolve disputed guidance:

- [Cucumber: Writing better Gherkin](https://cucumber.io/docs/bdd/better-gherkin/) — behavior and level of detail.
- [Gherkin reference](https://cucumber.io/docs/gherkin/reference/) and [grammar](https://github.com/cucumber/gherkin/blob/main/gherkin.berp) — constructs and syntax; the language does not limit scenarios to one `When`.
- [Cucumber: Anti-patterns](https://cucumber.io/docs/guides/anti-patterns/) — feature-coupled and conjunction steps.
- [Seb Rose: BRIEF](https://cucumber.io/blog/bdd/keep-your-scenarios-brief/) — essential detail, concrete examples, and brevity.
- [Matt Wynne: Example Mapping](https://cucumber.io/blog/bdd/example-mapping-introduction/) — rules, examples, and questions.
- [Dan North: What's in a Story?](https://dannorth.net/blog/whats-in-a-story/) — context, events, and outcomes.
- [Andy Knight: Writing Good Gherkin](https://automationpanda.com/2017/01/30/bdd-101-writing-good-gherkin/) — one behavior per scenario, step phrasing, and point of view.
