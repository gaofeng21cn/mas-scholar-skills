"""Options for kernel self-checks delegated to pytest."""


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--with-pillow",
        action="store_true",
        help="Exercise the Pillow figure-composition fixtures.",
    )
