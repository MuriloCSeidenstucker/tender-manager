import factory

from src.infra.entities import CompanyEntity


class CompanyFactory(factory.Factory):
    class Meta:
        model = CompanyEntity

    name = factory.Faker("text")
    trade_name = factory.Faker("text")
    cnpj = factory.Faker("text")
    user_id = 1
