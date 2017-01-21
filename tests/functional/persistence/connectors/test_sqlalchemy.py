# -*- coding: utf-8 -*-
from oldspeak.persistence.sql.models import User
from tests.functional.scenarios import sql_scenario


@sql_scenario
def test_mysql_connect(context):
    "Checking database querying"
    User.using(context.db.alias).all().should.be.empty
