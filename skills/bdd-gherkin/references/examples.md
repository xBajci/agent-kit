# Gherkin writing decisions

All business rules in these examples are illustrative. They are not requirements for any particular project.

## Rewrite a mechanical scenario

Established rule: an item's subtotal is its quantity multiplied by its unit price. A notebook costs $12.

Weak wording:

```gherkin
Feature: Shopping cart
  Scenario: Successful test
    Given the customer opens "/cart"
    When the customer clicks "#notebook"
    And the customer fills "#quantity" with "2"
    And the customer clicks "#save"
    Then the cart is correct
```

Clearer wording:

```gherkin
Feature: Shopping cart
  Rule: An item's subtotal reflects its quantity and unit price
    Scenario: Two notebooks at $12 have a subtotal of $24
      Given a notebook costs $12
      When the customer adds 2 notebooks to the cart
      Then the cart shows a notebook subtotal of $24
```

The important numbers remain visible. Replacing the form with another interface does not change the rule.

## An event can contain parameters

Established rule: a partial payment reduces an invoice's outstanding balance by the amount paid.

```gherkin
Feature: Partial invoice payments
  Scenario: A $40 payment reduces a $120 outstanding balance to $80
    Given the customer has an invoice with an outstanding balance of $120
    When the customer pays $40 toward the invoice
    Then the invoice summary shows an outstanding balance of $80
```

Moving the payment amount into `Given` would not improve this example. The example establishes no rule for overpayment.

## Use an outline for meaningful boundaries

Established rule: a workshop has 10 places. A new registration request is accepted if existing registrations plus the requested places do not exceed capacity; otherwise it is rejected.

```gherkin
Feature: Workshop registration
  Rule: Registration requests cannot exceed workshop capacity
    Scenario Outline: Decide a registration request using remaining capacity
      Given a workshop has 10 places
      And 8 places are already reserved
      When an organizer requests <places> additional places
      Then the registration request is "<result>"

      Examples:
        | places | result   |
        | 1      | accepted |
        | 2      | accepted |
        | 3      | rejected |
```

These examples show cases below, at, and above the boundary. Zero or negative quantities require their own established rule; do not invent one as part of this test.

## A table can express expected results

Established rule: the cart retains the names and quantities of added items. The customer adds two notebooks and one pen.

```gherkin
Feature: Cart summary
  Scenario: The summary contains the added items and their quantities
    When the customer adds 2 notebooks and 1 pen to an empty cart
    Then the cart summary contains exactly these items
      | item     | quantity |
      | notebook | 2        |
      | pen      | 1        |
```

The Data Table belongs to `Then` and does not multiply scenarios. Omitting `Given` is not a syntax error; add starting context when it affects the behavior.

## Ask only when a rule is missing

Request: "Premium customers receive a discount."

The rate and eligible purchases are missing. Ask: "What discount do premium customers receive, and which purchases qualify?"
Do not invent a ten-percent discount. If the request already specifies the rate and eligibility, proceed without asking again.

For time-sensitive rules, establish the relevant boundary and time zone when they affect the outcome. Resolving an ambiguity does not create an additional approval requirement.

## Select a language without tying it to the conversation

- A request written in a non-English language, with no language instructions or existing scenarios: write scenarios in English.
- Applicable project instructions require French, while older examples are English: write the requested scenarios in French.
- No language instructions, but the feature being edited is German: preserve German.
- The user explicitly asks for Spanish scenarios: use Spanish for the task, subject to applicable instruction precedence.

Preserve the relevant keyword dialect separately from the text language. An English-keyword feature can contain French step text; a feature using French keywords needs the appropriate `# language: fr` header.

## Keep the distinguishing condition out of the background

Established rules: the public calendar shows a blocked date as booked; the note on a blocked date is visible to the administrator only.

Weak wording hides the condition each example depends on, and mixes two behaviors with interface mechanics:

```gherkin
Feature: Blocked dates
  Background:
    Given the administrator is signed in
    And the administrator has blocked a date with the note "Owner's party"

  Scenario: Blocking
    When the administrator clicks "Blocked dates"
    And the visitor opens the home page
    Then day 12 has the class "cal-day--booked"
    And the note is not shown
```

Clearer wording keeps only the shared, non-distinguishing context in `Background`:

```gherkin
Feature: Blocked dates
  Rule: A blocked date shows as booked in the public calendar
    Background:
      Given the administrator is signed in

    Scenario: A blocked date shows as booked to visitors
      Given the administrator has blocked a date four months ahead
      When a visitor views the public calendar for that month
      Then the visitor sees that date as booked

    Scenario: The note on a blocked date stays private
      Given the administrator has blocked a date with the note "Owner's party"
      When a visitor views the public calendar for that month
      Then the visitor does not see the note anywhere
```

The note text stays visible in the second example because it is what must stay hidden. In the first example the note is incidental, so it is omitted.
