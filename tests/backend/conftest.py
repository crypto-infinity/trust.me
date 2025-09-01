import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--url",
        action="store",
        default=None,
        help="URL dell'endpoint da testare"
    )


@pytest.fixture
def url(request):
    return request.config.getoption("--url")
