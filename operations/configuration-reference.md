# Configuration Reference

**Status:** Placeholder — content lands as each service ships in Phases 1–6

The canonical reference for every environment variable, config flag, and tunable setting.

## Configuration philosophy

1. **Safe defaults** — out-of-the-box settings work in evaluation
2. **One way to configure** — each setting has one canonical source (environment variable)
3. **Explicit secrets** — secret values are never read from environment variables in production; the credential-broker handles secret retrieval
4. **Version compatibility** — config that worked in version N continues to work in N+1 with deprecation warnings
