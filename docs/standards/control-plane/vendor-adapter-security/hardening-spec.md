# Vendor Adapter Security Hardening Specification

This document captures our hardened implementation doctrine by extracting and correcting failure patterns observed in external vendor-adapter designs. It is not an upstream remediation plan and does not prescribe or advertise any specific third-party project.

## Goals

1. Fail closed on non-loopback startup without auth.
2. Remove ambient MCP capability widening.
3. Eliminate heuristic tool-call execution from model prose.
4. Reject duplicate tool names.
5. Isolate debug routes.
6. Preserve existing strengths: local-first defaults, honest 501s, remote MCP token-over-plaintext refusal, remote response size cap.

## Patch A — startup/auth/debug surface

### Files
- `Sources/CLI.swift`
- `Sources/Server.swift`
- `Sources/SecurityMiddleware.swift`
- `Sources/Core/OriginValidator.swift`
- `SECURITY.md`

### Required behavior
- If `host` is non-loopback and `token == nil`, startup fails unless `--allow-unauthenticated-bind` is present.
- `--debug` alone does not expose `/v1/logs*` remotely. Debug routes must be loopback-only unless `--debug-token` or equivalent is configured.
- Docs and CLI naming must match. Remove stale `--permissive` / `--dangerous-allow-all-origins` references.

### Suggested CLI additions
- `--allow-unauthenticated-bind`
- `--debug-token <secret>` or `--debug-loopback-only`
- `--mcp-auto-execute` default `false`

### Pseudocode
```swift
func validateServerConfig(_ config: ServerConfig) throws {
    let nonLoopback = !isLoopbackHost(config.host)
    if nonLoopback && config.token == nil && !config.allowUnauthenticatedBind {
        throw CLIError("Refusing non-loopback bind without --token. Use --allow-unauthenticated-bind to override.")
    }
    if config.debug && nonLoopback && config.debugToken == nil && !config.debugLoopbackOnly {
        throw CLIError("Refusing remote debug routes without --debug-token or --debug-loopback-only.")
    }
}
```

## Patch B — explicit tool scope + no heuristic execution

### Files
- `Sources/Handlers.swift`
- `Sources/Core/ToolCallHandler.swift`
- `Sources/Core/ChatRequestValidator.swift`

### Required behavior
- If request omits `tools`, effective executable tool scope is empty.
- Server-side MCP discovery may still appear in metadata or `/v1/models`, but not in executable request scope.
- `mcpAutoExecuteResponse` removed from default path.
- Tool execution only allowed when request includes an explicit execution mode and explicit tool allowlist.
- Tool intent must come from a dedicated structured field, not extracted from prose or markdown.

### Suggested request additions
- `x_execution_mode`: `plan_only | execute_approved`
- `x_allowed_tools`: `["toolA", "toolB"]`

### Pseudocode
```swift
let declaredTools = chatRequest.tools ?? []
let allowedToolNames = Set(chatRequest.x_allowed_tools ?? declaredTools.map { $0.function.name })
let effectiveTools = declaredTools.filter { allowedToolNames.contains($0.function.name) }

if chatRequest.x_execution_mode == .executeApproved {
    guard !effectiveTools.isEmpty else {
        throw OpenAIRequestError("Execution requested but no explicit tool scope provided")
    }
}
```

### Tool-call parsing changes
- Delete markdown fence extraction.
- Delete preamble scanning.
- Delete `ensureJSONArguments()` coercion of empty string or plain string.
- Require strict object shape:
  - `tool_calls` array present
  - each call has `id`, `type == "function"`, `function.name`, `function.arguments`
  - `function.arguments` parses as valid JSON object matching the tool schema

### Pseudocode
```swift
public static func parseExecutableToolCalls(_ json: String) throws -> [ParsedToolCall] {
    let data = Data(json.utf8)
    let envelope = try JSONDecoder().decode(StrictToolEnvelope.self, from: data)
    return try envelope.tool_calls.map { call in
        guard call.type == "function" else { throw ToolIntentError.unsupportedType }
        guard isValidJSONObject(call.function.arguments) else { throw ToolIntentError.invalidArguments }
        return ParsedToolCall(...)
    }
}
```

## Patch C — MCP routing and observability

### Files
- `Sources/MCPClient.swift`

### Required behavior
- Duplicate tool names fail startup.
- Local MCP stderr captured into bounded ring buffer in debug mode.
- Remote SSE parser becomes strict and event-aware.

### Duplicate handling pseudocode
```swift
for tool in conn.tools {
    if toolMap[tool.function.name] != nil {
        throw MCPError.processError("Duplicate MCP tool name: \(tool.function.name)")
    }
    toolMap[tool.function.name] = conn
}
```

### SSE handling pseudocode
```swift
let events = try SSEParser.parse(raw)
let dataEvents = events.filter { $0.event == nil || $0.event == "message" }
let payloads = dataEvents.compactMap(\ .data).filter { !$0.isEmpty }
guard payloads.count == 1 else {
    throw MCPError.serverError("Expected exactly one JSON payload event from remote MCP server")
}
return payloads[0]
```

## Patch D — tests and docs

### New tests
- `ChatRequestValidatorTests.swift`
- `ServerSecurityPolicyTests.swift`
- `MCPManagerTests.swift`
- `ToolIntentStrictParsingTests.swift`

### Test matrix
1. Non-loopback bind without token => startup failure.
2. Debug routes unavailable remotely without debug auth/scope.
3. Omitted `tools` => no executable tools even when MCP attached.
4. JSON in markdown fence => not executable.
5. Preamble + JSON => not executable.
6. Empty arguments string => validation failure.
7. Plain-string arguments => validation failure.
8. Duplicate MCP tool names => startup failure.
9. Remote MCP token over non-loopback HTTP => refusal retained.
10. Remote MCP response over 10 MB => refusal retained.

## Minimal sequencing
1. Patch A first.
2. Patch B second.
3. Patch C third.
4. Patch D fourth.

## Acceptance gates
- No remote bind without auth unless explicitly unsafe.
- No ambient tool execution.
- No heuristic executable parsing from prose.
- No duplicate tool routing.
- Debug surface separately protected.
- Existing transport protections retained.
