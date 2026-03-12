"""Capture response bodies from Betano.ng initial page load API calls."""
import json
import asyncio
from playwright.async_api import async_playwright

TARGETS = {
    "top-events-v2": "/api/home/top-events-v2",
    "leagues": "/api/static-content/assets/leagues",
    "regions": "/api/static-content/assets/regions",
    "betofday": "/api/betofday/all",
    "live-overview": "/danae-webapi/api/live/overview/latest",
    "layout-live": "/danae-webapi/api/layout/live",
}

captured = {}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context(
            locale="en-NG",
            timezone_id="Africa/Lagos",
            viewport={"width": 1280, "height": 900},
        )
        page = await ctx.new_page()

        async def on_response(resp):
            url = resp.url
            for name, pattern in TARGETS.items():
                if pattern in url and name not in captured:
                    try:
                        status = resp.status
                        if status == 200:
                            body = await resp.body()
                            if len(body) > 10:
                                captured[name] = {
                                    "url": url,
                                    "status": status,
                                    "size": len(body),
                                    "body": body.decode("utf-8", errors="replace"),
                                }
                                print(f"  Captured [{status}] {name} ({len(body)}B)")
                    except Exception as e:
                        print(f"  Error capturing {name}: {e}")

        page.on("response", on_response)

        print("=== Loading betano.ng homepage ===")
        try:
            await page.goto("https://www.betano.ng/", wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"  Navigation: {e}")

        # Wait for API calls to complete
        print("=== Waiting for API calls... ===")
        await asyncio.sleep(15)

        print(f"\n=== Captured {len(captured)} responses ===")
        for name, data in captured.items():
            print(f"  {name}: {data['size']}B from {data['url'][:100]}")
            with open(f"betano_{name}.json", "w", encoding="utf-8") as f:
                try:
                    parsed = json.loads(data["body"])
                    json.dump(parsed, f, indent=2, ensure_ascii=False)
                    print(f"    -> saved betano_{name}.json (valid JSON)")
                except json.JSONDecodeError:
                    f.write(data["body"][:5000])
                    print(f"    -> saved betano_{name}.json (raw text)")

        # Also try to directly fetch top-events from browser context
        if "top-events-v2" not in captured:
            print("\n=== Trying direct fetch from browser context ===")
            try:
                result = await page.evaluate("""
                    async () => {
                        try {
                            const r = await fetch('/api/home/top-events-v2?req=s,stnf,c,mb,mbl');
                            return { status: r.status, body: await r.text() };
                        } catch(e) {
                            return { error: e.message };
                        }
                    }
                """)
                print(f"  Direct fetch result: status={result.get('status')}, size={len(result.get('body',''))}B")
                if result.get("status") == 200:
                    with open("betano_top-events-v2.json", "w") as f:
                        f.write(result["body"])
                    print("    -> saved betano_top-events-v2.json")
            except Exception as e:
                print(f"  Direct fetch error: {e}")

        await browser.close()

    print("\n=== Summary ===")
    for name in TARGETS:
        if name in captured:
            print(f"  OK   {name}: {captured[name]['size']}B")
        else:
            print(f"  MISS {name}")

asyncio.run(main())
