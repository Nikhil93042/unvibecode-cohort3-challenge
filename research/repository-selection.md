# Selected Evaluation Repositories

To rigorously test UnvibeCode across diverse software designs, language ecosystems, symbol linking models, and business logic paradigms, we selected three distinct public open-source repositories:

| Repository | Ecosystem / Language | Commit Hash | Source Files | Estimated Tokens | Architectural Focus |
|---|---|---|---|---|---|
| **[encode/starlette](https://github.com/encode/starlette)** | Python (Async / ASGI) | `0f08970e5cce0aec4fc1cea7447c262d741795eb` | 88 | ~263,131 | Asynchronous request-response pipelines, ASGI middleware stacks, endpoint routing tables, background tasks, authentication & session state handling. |
| **[pallets/flask](https://github.com/pallets/flask)** | Python (WSGI / Synchronous) | `49943b5a94413a530761350f04e896f76e8d620e` | 105 | ~194,479 | Synchronous WSGI dispatch, context locals (`g`, `request`, `session`), blueprint registration, error handlers, signal dispatching. |
| **[auth0/node-jsonwebtoken](https://github.com/auth0/node-jsonwebtoken)** | JavaScript / TypeScript | `b924272f29192e12926b5414546f7c5bfcc9579d` | 46 | ~49,220 | Cryptographic token creation and signature verification (`sign`, `verify`, `decode`), claim validation (exp, nbf, aud, iss), key handling, and Tree-sitter JS AST parsing. |

## Rationale for Selection
1. **Different Concurrency & Architecture Paradigms**:
   - Starlette tests async execution paths (`async def`, `await`, lifespan context managers, ASGI middleware chains).
   - Flask tests traditional synchronous WSGI patterns, thread locals, and decorator-driven blueprints.
   - Node-jsonwebtoken tests cryptographic security-critical workflows and JavaScript/Tree-sitter module import/export semantics.
2. **Repository Token Boundaries**:
   - All three repositories are well under the 2,000,000 token threshold. This guarantees that UnvibeCode will execute both Track A (Connected Code Map) and Track B (Business Workflows and Risk Review) without being truncated to Fast Lane only.
3. **Reproducibility**:
   - Each repository is pegged to an immutable git commit hash, enabling 100% deterministic external reproduction by evaluating engineers.