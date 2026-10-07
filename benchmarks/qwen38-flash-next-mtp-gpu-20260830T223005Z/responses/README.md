# Responses

No response payload exists. The controlled MTP server exited during draft-model
loading, before it opened the HTTP endpoint. Formal deterministic and reasoning
requests were not sent because the mandatory early-stop condition had already
been established. The prepared request bodies remain in `../commands/` for a
future runtime with working Qwen4Exp MTP support.
