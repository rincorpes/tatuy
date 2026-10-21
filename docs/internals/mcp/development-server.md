# Development Server

The Tatuy development server exposes project-inspection operations such as:

```text
list projects
list files
read file
search code
server information
```

The intended workflow is:

```text
AI request
   ↓
inspect AGENTS.md
   ↓
inspect relevant source/docs/examples
   ↓
reason in chat
   ↓
user reviews/applies changes
```

Read-only access is deliberate.

It allows useful project grounding while keeping repository modification under developer control.

---
