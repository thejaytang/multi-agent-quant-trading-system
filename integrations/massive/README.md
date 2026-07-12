# Massive integration

Local stub only. No external API calls are made unless the runtime is explicitly configured for external requests.

## Official AI documentation indexes

- REST API llms index: https://massive.com/docs/rest/llms.txt
- WebSocket llms index: https://massive.com/docs/websocket/llms.txt
- Full documentation llms index: https://massive.com/docs/llms.txt
- MCP repository: https://github.com/massive-com/mcp_massive

## First supported REST endpoints

- Stocks custom OHLC bars: `GET /v2/aggs/ticker/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}`
- Stocks news: `GET /v2/reference/news`

## Safety policy

Keep `MASSIVE_API_KEY` only in `.env.local` or process environment. Do not commit real credentials. Keep `EXTERNAL_API_REQUESTS_ENABLED=false` until the user explicitly asks for a live read-only connectivity test.
