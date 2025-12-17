import typing


class Injector:
    def __init__(self):
        self.services: dict[type, typing.Any] = {}
        self.factories: dict[type, typing.Callable[[typing.Self], typing.Any]] = {}

    def get_service(self, service_type: type) -> typing.Any:
        if service_type not in self.services:
            if service_type not in self.factories:
                raise ValueError(f"No factory found for service type: {service_type}")
            factory = self.factories[service_type]
            self.services[service_type] = factory(self)
        return self.services[service_type]

    def add_service(self, service: typing.Any):
        self.services[type(service)] = service

    def add_factory(
        self, type: type, factory: typing.Callable[[typing.Self], typing.Any]
    ):
        self.factories[type] = factory

    def create_scope(self):
        scope = Injector()
        scope.factories = self.factories.copy()
        scope.services = self.services.copy()
        return scope
