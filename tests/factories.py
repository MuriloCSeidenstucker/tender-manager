from datetime import datetime

import factory

from src.infra.entities import (
    CompanyEntity,
    TenderEntity,
    TenderFormat,
    TenderModality,
    TenderStatus,
)


class CompanyFactory(factory.Factory):
    class Meta:
        model = CompanyEntity

    name = factory.Faker("text")
    trade_name = factory.Faker("text")
    cnpj = factory.Faker("text")
    user_id = 1


class TenderFactory(factory.Factory):
    class Meta:
        model = TenderEntity

    tender_number = factory.Sequence(lambda n: n + 1)
    tender_year = 2026
    object_description = factory.Faker("sentence")
    public_body_name = factory.Faker("company")
    modality = factory.Iterator(list(TenderModality))
    format = factory.Iterator(list(TenderFormat))
    status = factory.Iterator(list(TenderStatus))
    participation_result = None
    awarded_value = None
    session_date = factory.LazyFunction(datetime.utcnow)
    company_id = 1
