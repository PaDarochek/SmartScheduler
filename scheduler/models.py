import yougile
import yougile.models as models


class AppLogicModel:
    def __init__(self):
        self.token = ""

    def auth(self, login: str, password: str, company_name: str):
        """Authorize to YouGile

        :param login: User login
        :type login: str
        :param password: User password
        :type password: str
        :param company_name: Company name
        :type company_name: str
        :raises ValueError: Authorization error
        """
        model = models.AuthKeyController_companiesList(
            login=login, password=password, name=company_name
        )
        response = yougile.query(model)
        if response.status_code != 200:
            raise ValueError()

        companies = response.json()["content"]
        if len(companies) != 1:
            raise ValueError()
        company_id = companies[0]["id"]

        model = models.AuthKeyController_create(
            login=login, password=password, companyId=company_id
        )
        response = yougile.query(model)
        if response.status_code != 200:
            raise ValueError()
        self.token = response.json()["key"]
