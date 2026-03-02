# Acceptance Criteria Guide

## What is Acceptance Criteria?

Acceptance criteria (AC) define the conditions that must be satisfied for a user story or feature to be considered complete.

## Seven Dimensions of AC

1. **Functionality**: What the system must do
2. **Data**: What data is processed/stored
3. **User Experience**: How users interact with the feature
4. **Performance**: Response time, throughput
5. **Security**: Authentication, authorization, data protection
6. **Compatibility**: Browser, device, API versions
7. **Error Handling**: How errors are managed

## AC Format

```
GIVEN [precondition]
WHEN [action]
THEN [expected outcome]
```

## Examples

### Login Feature
```
GIVEN a registered user
WHEN they enter valid credentials
THEN they are redirected to the dashboard

GIVEN a registered user
WHEN they enter invalid credentials
THEN an error message is displayed
```

### Search Feature
```
GIVEN a user on the search page
WHEN they type a search query
THEN results appear within 500ms

GIVEN a user with no results
THEN a "no results" message is shown
```

## Best Practices

- Start with positive scenarios
- Cover negative/error cases
- Be specific and measurable
- Keep ACs independent
- Test each criterion independently
