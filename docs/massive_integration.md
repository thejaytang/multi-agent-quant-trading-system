# Massive Integration

Massive is the primary market data and news source for this project.

Official AI-readable documentation indexes:

- REST API: https://massive.com/docs/rest/llms.txt
- WebSocket: https://massive.com/docs/websocket/llms.txt
- Full docs: https://massive.com/docs/llms.txt
- MCP: https://github.com/massive-com/mcp_massive

The first integration phase should use REST only and stay read-only:

- Stocks custom OHLC bars: `GET /v2/aggs/ticker/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}`
- Stocks news: `GET /v2/reference/news`

Do not enable real-time WebSocket or MCP access until the REST client, data quality checks, rate-limit handling, and cache policy are verified.

Keep `MASSIVE_API_KEY` in `.env.local` or process environment. Do not commit credentials.
