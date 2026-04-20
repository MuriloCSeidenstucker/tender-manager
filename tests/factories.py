from datetime import datetime

import factory
from faker import Faker

from src.infra.entities import (
    CompanyEntity,
    TenderEntity,
    TenderFormat,
    TenderModality,
    TenderStatus,
    UserEntity,
)

fake = Faker()


class UserFactory(factory.Factory):
    class Meta:
        model = UserEntity

    username = factory.Sequence(lambda n: f"test{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")
    password = factory.LazyAttribute(lambda obj: f"{obj.username}testpassword")


class CompanyFactory(factory.Factory):
    class Meta:
        model = CompanyEntity

    name = factory.LazyAttribute(lambda _: fake.company()[:150])
    trade_name = factory.LazyAttribute(lambda _: fake.company()[:150])
    cnpj = factory.Sequence(lambda n: f"{n:014d}")
    user_id = 1


class TenderFactory(factory.Factory):
    class Meta:
        model = TenderEntity

    tender_number = factory.Sequence(lambda n: n + 1)
    tender_year = 2026
    object_description = factory.LazyAttribute(lambda _: fake.company()[:500])
    public_body_name = factory.LazyAttribute(lambda _: fake.company()[:150])
    modality = factory.Iterator(list(TenderModality))
    format = factory.Iterator(list(TenderFormat))
    status = factory.Iterator(list(TenderStatus))
    participation_result = None
    awarded_value = None
    session_date = factory.LazyFunction(datetime.utcnow)
    company_id = 1
