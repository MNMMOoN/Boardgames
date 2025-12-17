def main() -> None:
    from morghi.services import MorghiApp
    from morghi.core import Injector, MorghiConfig
    import os

    injector = Injector()
    injector.add_factory(
        MorghiConfig,
        lambda i: MorghiConfig(
            port=int(os.environ.get("MORGHI_PORT", 8080)),
            jwt_secret=os.environ.get(
                "MORGHI_JWT_SECRET_KEY", "super-secret-key-that-no-one-knows"
            ),
        ),
    )
    injector.add_factory(MorghiApp, lambda i: MorghiApp(__name__, i))
    app: MorghiApp = injector.get_service(MorghiApp)
    app.run()
