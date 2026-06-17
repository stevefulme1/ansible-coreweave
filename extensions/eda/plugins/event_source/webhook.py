# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""CoreWeave webhook event source for ansible-rulebook.

Listens for incoming HTTP POST requests (e.g., from CoreWeave Grafana
alerts, Prometheus Alertmanager, or custom webhooks) and emits events
to the rulebook engine.

Usage in a rulebook:
  sources:
    - stevefulme1.coreweave.webhook:
        host: 0.0.0.0
        port: 5000
        token: "{{ webhook_secret }}"
"""

from __future__ import (absolute_import, division, print_function)
from __future__ import annotations

__metaclass__ = type

import asyncio
import json
import logging
from typing import Any

from aiohttp import web

logger = logging.getLogger(__name__)


async def main(queue: asyncio.Queue, args: dict[str, Any]) -> None:
    """Entry point for the EDA event source plugin.

    Args:
        queue: asyncio.Queue to put events onto for the rulebook engine.
        args: Configuration dict from the rulebook source definition.
    """
    host = str(args.get("host", "0.0.0.0"))  # noqa: S104
    port = int(args.get("port", 5000))
    token = args.get("token")

    app = web.Application()
    handler = WebhookHandler(queue, token)
    app.router.add_post("/", handler.handle)
    app.router.add_post("/{path:.*}", handler.handle)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info("CoreWeave webhook listener started on %s:%d", host, port)

    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("Shutting down webhook listener")
    finally:
        await runner.cleanup()


class WebhookHandler:
    """Handle incoming webhook POST requests."""

    def __init__(self, queue: asyncio.Queue, token: str | None = None) -> None:
        self.queue = queue
        self.token = token

    async def handle(self, request: web.Request) -> web.Response:
        """Process an incoming webhook request."""
        if self.token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header != f"Bearer {self.token}":
                return web.Response(status=401, text="Unauthorized")

        try:
            payload = await request.json()
        except json.JSONDecodeError:
            body = await request.text()
            payload = {"raw": body}

        event = {
            "coreweave": {
                "payload": payload,
                "headers": dict(request.headers),
                "path": str(request.path),
                "method": request.method,
            }
        }

        await self.queue.put(event)
        return web.Response(status=200, text="OK")


if __name__ == "__main__":

    class MockQueue:
        async def put(self, event: Any) -> None:
            print(json.dumps(event, indent=2))

    asyncio.run(main(MockQueue(), {"host": "0.0.0.0", "port": 5000}))
