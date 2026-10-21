# Implementing a Backend

A custom backend should:

1. define configuration
2. implement capabilities
3. compose them behind the backend contract
4. implement a builder
5. register the builder

Preserve these rules:

- do not leak implementation-specific types upward
- keep capabilities focused
- depend on the smallest interface
- contain platform-specific complexity inside the backend

The former `docs/001_backend/development.md` should migrate here.

---
