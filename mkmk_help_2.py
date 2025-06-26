import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main() -> None:
    logger.info("start mkmk_help_2")

    logger.info("end mkmk_help_2")


if __name__ == "__main__":
    main()
