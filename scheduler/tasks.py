import yougile
import yougile.models as models


class UnauthorizedError(Exception):
    pass


class ForbiddenError(Exception):
    pass


class HTTPError(Exception):
    pass


class Tasks:
    """Representation of app logic"""

    def auth(self, login: str, password: str, company_name: str):
        """Authorize to YouGile

        :param login: User login
        :type login: str
        :param password: User password
        :type password: str
        :param company_name: Company name
        :type company_name: str
        :raises UnauthorisedError: Response 401
        :raises ForbiddenError: Response 403
        :raises HTTPError: Response 429
        :raises ValueError: No company with name `company_name`
        """
        model = models.AuthKeyController_companiesList(
            login=login, password=password, name=company_name
        )
        response = yougile.query(model)
        status = response.status_code
        if status == 401:
            raise UnauthorizedError("Unauthorized")
        elif status == 403:
            raise ForbiddenError("Forbidden")
        elif status == 429:
            raise HTTPError("HTTP error")

        companies = response.json()["content"]
        if len(companies) != 1:
            raise ValueError(f"No company with name {company_name}")
        company_id = companies[0]["id"]

        model = models.AuthKeyController_create(
            login=login, password=password, companyId=company_id
        )
        response = yougile.query(model)
        self.token = response.json()["key"]
