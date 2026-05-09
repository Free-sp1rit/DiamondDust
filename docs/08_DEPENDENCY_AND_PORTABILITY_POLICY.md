# Dependency and Portability Policy

## Dependency Principle

Core domain logic must survive replacement of:

- LLM provider
- structured output library
- vector database
- UI framework
- note-taking platform
- agent protocol

## Dependency Categories

### Core Dependencies

Allowed only if stable and hard to replace:

- Python
- Pydantic
- Markdown parser
- SQLite

### Adapter Dependencies

Allowed behind interfaces:

- OpenAI SDK
- Anthropic SDK
- Gemini SDK
- LiteLLM
- Instructor
- LanceDB
- Obsidian API
- Notion API
- MCP SDK

## New Dependency Rule

A new dependency requires:

- purpose
- alternatives considered
- replacement strategy
- affected layer
- test impact
- portability impact
- security impact
- maintenance impact

## Dependency Autonomy

The agent may choose internal implementation techniques autonomously.

The agent must request escalation before adding a production dependency when the dependency affects:

- portability
- security
- deployment
- runtime cost
- external service lock-in
- public schema
- core architecture
- long-term maintenance

Development-only dependencies may be added without user approval if they are low risk, documented, and do not affect runtime behavior, but they must still be included in dependency notes or project tooling docs.

## Forbidden

- provider SDK in domain core
- direct vector DB calls in business logic
- UI framework assumptions in domain model
- persistence logic tied to one proprietary platform
- runtime behavior that depends on a single vendor without an adapter boundary

## Replacement Strategy

Every external service or vendor-specific library must be accessed through an interface or adapter.
