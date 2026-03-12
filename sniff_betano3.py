"""Try to find per-league event API endpoints on Betano.ng from browser context."""
import json
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context(
            locale="en-NG",
            timezone_id="Africa/Lagos",
            viewport={"width": 1280, "height": 900},
        )
        page = await ctx.new_page()

        print("=== Loading homepage ===")
        await page.goto("https://www.betano.ng/", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)

        # Try various API patterns for Premier League events
        endpoints = [
            # Known Kaizen API patterns
            "/api/sport/football/premier-league-england/?req=tn,stnf,c,mb,mbl",
            "/api/sport/football/leagues/1636/?req=tn,stnf,c,mb,mbl",
            "/api/sport/football/?req=tn,stnf,c,mb,mbl",
            "/api/sport/football/upcoming-matches-today/?req=tn,stnf,c,mb,mbl",
            # danae-webapi patterns
            "/danae-webapi/api/eventlist?sportId=1&zoneId=1&languageId=1&operatorId=15",
            "/danae-webapi/api/events?sportId=1&leagueId=1636&languageId=1&operatorId=15",
            # Try zone/league combos
            "/api/sport/football/england/?req=tn,stnf,c,mb,mbl",
            "/api/sport/football/england/premier-league/?req=tn,stnf,c,mb,mbl",
            # Try the top-events with sport filter
            "/api/home/top-events-v2?req=s,stnf,c,mb,mbl&sportId=FOOT",
            # Match odds API
            "/api/sport/football/premier-league-england/1636/?req=tn,stnf,c,mb,mbl",
        ]

        print("\n=== Testing API endpoints ===")
        for ep in endpoints:
            try:
                result = await page.evaluate(f"""
                    async () => {{
                        try {{
                            const r = await fetch('{ep}');
                            const text = await r.text();
                            return {{ status: r.status, size: text.length, body: text.substring(0, 500) }};
                        }} catch(e) {{
                            return {{ error: e.message }};
                        }}
                    }}
                """)
                status = result.get("status", "err")
                size = result.get("size", 0)
                body_preview = result.get("body", "")[:200]
                error = result.get("error", "")
                if error:
                    print(f"  ERR  {ep}")
                    print(f"       {error[:100]}")
                elif status == 200 and size > 100:
                    print(f"  [{status}] ({size}B) {ep}")
                    print(f"       {body_preview[:150]}")
                else:
                    print(f"  [{status}] ({size}B) {ep}")
                    if size < 500:
                        print(f"       {body_preview[:150]}")
            except Exception as e:
                print(f"  FAIL {ep}: {e}")

        # Also capture all cookies and headers for potential direct requests
        cookies = await ctx.cookies()
        print(f"\n=== Cookies ({len(cookies)}) ===")
        for c in cookies:
            print(f"  {c['name']}: {c['value'][:50]}...")

        await browser.close()

asyncio.run(main())
