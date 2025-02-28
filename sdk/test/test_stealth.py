import json

import pytest

from harambe.contrib import playwright_harness


@pytest.fixture
async def async_page():
    async with playwright_harness(
        headless=True, enable_clipboard=True, browser_type="chromium"
    ) as page_factory:
        yield await page_factory()


@pytest.mark.asyncio
async def test_navigator_webdriver(async_page):
    await async_page.goto("https://kaliiiiiiiiii.github.io/brotector/?crash=false")

    # Site contains a button to save the results as JSON
    await async_page.get_by_role("button", name="copy as JSON").click()
    clipboard = await async_page.evaluate("navigator.clipboard.readText()")
    stealth_results = json.loads(clipboard)

    # There are many different checks on the site. But we're focusing our attention on specific ones that we already fix
    # TODO: Add more checks as needed
    detections_to_avoid = [
        "navigator.webdriver",
    ]

    assert not any(
        result["detection"] in detections_to_avoid for result in stealth_results
    ), "A detection that should be avoided was found in the results"


@pytest.mark.asyncio
async def test_user_agent(async_page):
    user_agent = await async_page.evaluate("navigator.userAgent")
    assert (
        "headless" not in user_agent.lower()
    ), "User agent should not contain 'headless'"


@pytest.mark.asyncio
async def test_window_chrome(async_page):
    has_chrome = await async_page.evaluate("!!window.chrome")
    assert has_chrome, "window.chrome should be present in non-headless Chrome"


@pytest.mark.asyncio
async def test_plugins(async_page):
    plugins_length = await async_page.evaluate("navigator.plugins.length")
    assert plugins_length > 0, "Non-headless browsers should have at least one plugin"


@pytest.mark.asyncio
async def test_app_version(async_page):
    app_version = await async_page.evaluate("navigator.appVersion")
    assert (
        "headless" not in app_version.lower()
    ), "App version should not contain 'headless'"


@pytest.mark.asyncio
async def test_notification_permissions(async_page):
    permission_status = await async_page.evaluate("""
    async () => {
        const permissionStatus = await navigator.permissions.query({name: 'notifications'});
        return {
            notificationPermission: Notification.permission,
            permissionState: permissionStatus.state
        };
    }
    """)

    assert not (
        permission_status["notificationPermission"] == "denied"
        and permission_status["permissionState"] == "prompt"
    ), "Notification permissions should not be in an inconsistent state"


@pytest.mark.asyncio
async def test_connection_rtt(async_page):
    connection_rtt = await async_page.evaluate("""
    () => {
        const connection = navigator.connection;
        return connection ? connection.rtt : undefined;
    }
    """)

    assert (
        connection_rtt is not None and connection_rtt != 0
    ), "Connection RTT should exist and not be zero in non-headless browsers"
