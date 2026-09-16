"""Pytest configuration and fixtures."""

import logging
import os

import pytest

from playwright.sync_api import Page

from config.config_reader import config

from pages.dashboard_page import DashboardPage

from pages.login_page import LoginPage

from utils.test_data_reader import test_data


logger = logging.getLogger("orangehrm_tests")

logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
    )
    logger.addHandler(handler)


def pytest_addoption(parser):
    """Add a pytest CLI option to select the environment."""
    parser.addoption(
        "--env",
        action="store",
        default=None,
        help="Select environment: dev, qa, uat, prod",
    )


@pytest.fixture(scope="session", autouse=True)
def configure_environment(request):
    """Apply the environment selected through pytest CLI."""
    selected_env = request.config.getoption("--env")

    if selected_env:
        config.set_environment(selected_env)
        os.environ["TEST_ENV"] = config.current_env

    return config


@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Configure the Playwright browser launcher."""
    return {
        "headless": False,
        "slow_mo": int(os.getenv("SLOW_MO", "0")),
    }


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """Return a LoginPage object for the current test."""
    return LoginPage(page)


@pytest.fixture(scope="function")
def dashboard_page(page: Page) -> DashboardPage:
    """Return a DashboardPage object for the current test."""
    return DashboardPage(page)


@pytest.fixture(scope="session")
def valid_user():
    """Return valid login credentials."""
    return test_data.get_user("valid_user")


@pytest.fixture(scope="session")
def invalid_user():
    """Return invalid login credentials."""
    return test_data.get_user("invalid_user")


@pytest.fixture(scope="function")
def logged_in_page(
    page: Page,
    login_page: LoginPage,
    dashboard_page: DashboardPage,
    valid_user: dict,
) -> Page:
    """
    Login before each test and return an authenticated page.
    No saved Playwright authentication state is used.
    """
    logger.info("Starting login for test.")

    login_page.navigate(config.base_url)

    login_page.verify_login_page()

    login_page.login(
        valid_user["username"],
        valid_user["password"],
    )

    dashboard_page.verify_dashboard()

    logger.info("Login successful. Dashboard is visible.")

    return page


@pytest.fixture(autouse=True)
def capture_screenshot_on_failure(request, page: Page):
    """Capture a screenshot when a test fails."""
    yield

    if (
        hasattr(request.node, "rep_call")
        and request.node.rep_call.failed
    ):
        screenshot_path = (
            f"test-results/screenshots/"
            f"{request.node.name}.png"
        )

        os.makedirs(
            os.path.dirname(screenshot_path),
            exist_ok=True,
        )

        page.screenshot(
            path=screenshot_path,
            full_page=True,
        )

        print(
            f"\nScreenshot saved: {screenshot_path}"
        )


@pytest.hookimpl(
    tryfirst=True,
    hookwrapper=True,
)
def pytest_runtest_makereport(item, call):
    """Store test result information on the test item."""
    outcome = yield

    rep = outcome.get_result()

    setattr(
        item,
        f"rep_{rep.when}",
        rep,
    )


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Log the test that is starting."""
    logger.info(
        "Starting test: %s",
        item.nodeid,
    )


def pytest_collection_modifyitems(config, items):
    """
    Control test execution order.

    Priority:
    1. Login
    2. Buzz
    3. Vacancy
    4. Any other test modules alphabetically
    """

    def test_order(item):
        nodeid = item.nodeid.replace("\\", "/").lower()

        if "tests/login/test_auth_setup.py" in nodeid:
            return 0

        if "tests/login/test_login_logout.py" in nodeid:
            return 1

        if "tests/buzz/" in nodeid:
            return 2

        if "tests/vacancy/" in nodeid:
            return 3

        return 4, nodeid

    items.sort(
        key=lambda item: (
            test_order(item)
            if isinstance(test_order(item), tuple)
            else (test_order(item), item.nodeid)
        )
    )