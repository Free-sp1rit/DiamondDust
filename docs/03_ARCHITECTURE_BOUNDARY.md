# Architecture Boundary

## Architecture Style

Ports and Adapters / Hexagonal Architecture.

## Layers

1. Domain Core
2. Application Pipeline
3. AI Adapter
4. Storage Adapter
5. Interface Adapter

## Dependency Rule

Allowed:

- Interface → Application
- Application → Domain
- Application → Ports
- Adapter → Ports
- Adapter → External SDK

Forbidden:

- Domain → OpenAI / Anthropic / Gemini
- Domain → Obsidian / Notion / MCP
- Domain → FastAPI
- Domain → SQLite / LanceDB
- UI → provider SDK directly
- Storage adapter → business decision logic

## Core Responsibility

Domain Core defines:

- KnowledgeUnit
- Relation
- KnowledgePatch
- validation rules
- status rules
- source reference rules

Application Pipeline coordinates:

- parse
- extract
- normalize
- validate
- propose
- review
- commit

AI Adapter handles:

- model provider calls
- structured output
- retry
- model routing

Storage Adapter handles:

- Markdown read/write
- SQLite indexing
- vector index
- Git integration

Interface Adapter handles:

- CLI
- Web UI
- Obsidian plugin
- MCP server