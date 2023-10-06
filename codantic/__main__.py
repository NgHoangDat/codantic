def main():
    from mousse import get_logger
    from .app import app

    logger = get_logger("app")
    logger.include_extra = False
    logger.add_handler("RotatingFileHandler", path="logs/app.out")

    app()


if __name__ == "__main__":
    main()
