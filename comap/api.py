"""
comap.api module
"""
import logging
import os

import requests
import timestring

from .constants import AUTHORIZATION, COMAP_KEY, IDENTITY_URL, TIMEOUT, WSV_URL

_LOGGER = logging.getLogger(__name__)


class ErrorGettingData(Exception):
    """Raised when we cannot get data from API"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ComApCloud:
    """Create ComAp Cloud API instance"""

    def __init__(self, headers: dict) -> None:
        """Create ComAp Cloud API instance"""
        self._headers = headers

    def _get_api(
        self,
        application: dict,
        api: str,
        login_id: str | None = None,
        unit_guid: str | None = None,
        payload: dict | None = None,
    ) -> dict | None:
        """Call ComAp get API. Return response JSON, None if not succesfull"""
        if api not in application:
            _LOGGER.error("Unknown API %s!", api)
            return None
        try:
            if login_id is None:
                _url = application[api]
            elif unit_guid is None:
                _url = application[api].format(login_id)
            else:
                _url = application[api].format(login_id, unit_guid)
            body = {} if payload is None else payload
            try:
                response = requests.get(
                    _url, headers=self._headers, params=body, timeout=TIMEOUT
                )
            except requests.exceptions.Timeout:
                _LOGGER.error("API get %s response time-out.", api)
                return None
            _LOGGER.debug("Calling API url %s", response.url)
            if response.status_code != 200:
                _LOGGER.error(
                    "API %s returned code: " "%s (%s) ",
                    api,
                    response.status_code,
                    response.reason,
                )
                return None
        except Exception as e:
            _LOGGER.error("API %s error %s", api, e)
            return None
        return response.json()

    def _post_api(
        self,
        application: dict,
        api: str,
        login_id: str | None = None,
        unit_guid: str | None = None,
        payload: dict | None = None,
    ) -> dict | None:
        """Call ComAp post API. Return response JSON, None if not succesfull"""
        if api not in application:
            _LOGGER.error("Unknown API %s!", api)
            return None
        try:
            if login_id is None:
                _url = application[api]
            elif unit_guid is None:
                _url = application[api].format(login_id)
            else:
                _url = application[api].format(login_id, unit_guid)
            body = {} if payload is None else payload
            try:
                response = requests.post(
                    _url, headers=self._headers, json=body, timeout=TIMEOUT
                )
            except requests.exceptions.Timeout:
                _LOGGER.error("API post %s response time-out.", api)
                return None
            _LOGGER.debug("Calling API url %s", response.url)
            if response.status_code != 200:
                _LOGGER.error(
                    "API %s returned code: " "%s (%s) ",
                    api,
                    response.status_code,
                    response.reason,
                )
                return None
        except Exception as e:
            _LOGGER.error("API %s error %s", api, e)
            return None
        return response.json()


class Identity(ComApCloud):
    """Create ComAp Cloud Identity API instance"""

    def __init__(self, key: str) -> None:
        """Setup of the ComAp Cloud Identity API class"""
        super().__init__({"Content-Type": "application/json", COMAP_KEY: key})

    def get_api(self, api: str, payload: dict = None) -> str | dict:
        """Call ComAp Identity get API. Return response JSON if succesfull, None if not succesfull"""
        response = self._get_api(application=IDENTITY_URL, api=api, payload=payload)
        return None if response is None else response

    def post_api(self, api: str, payload: dict = None) -> str | dict:
        """Call ComAp Identity post API. Return response JSON if succesfull, None if not succesfull"""
        response = self._post_api(application=IDENTITY_URL, api=api, payload=payload)
        return None if response is None else response

    def authenticate(self, client_id: str, secret: str) -> dict | None:
        """Authenticate and return bearer token dictinary. The token is in ['access_token']"""
        body = {"clientId": client_id, "secret": secret}
        return self.post_api(api="authenticate", payload=body)


class WSV(ComApCloud):
    """Constructor"""

    def __init__(self, login_id: str, key: str, token: str) -> None:
        """Create WSV API instance"""
        self.__login_id = login_id
        super().__init__(
            {
                "Content-Type": "application/json",
                COMAP_KEY: key,
                AUTHORIZATION: "Bearer " + token,
            }
        )

    def get_api(
        self,
        api: str,
        unit_guid: str | None = None,
        file_name: str | None = None,
        payload: dict = None,
    ) -> dict | None:
        """Call WSV API. Return response JSON, None if not succesfull"""
        response = self._get_api(
            application=WSV_URL,
            api=api,
            login_id=self.__login_id,
            unit_guid=unit_guid,
            file_name=file_name,
            payload=payload,
        )
        return None if response is None else response

    def post_api(
        self, api: str, unit_guid: str | None = None, payload: dict = None
    ) -> dict | None:
        """Call ComAp API. Return response JSON, None if not succesfull"""

        response = self._post_api(
            application=WSV_URL,
            api=api,
            login_id=self.__login_id,
            unit_guid=unit_guid,
            payload=payload,
        )
        return None if response is None else response

    def units(self) -> list:
        """Get list of all units - returns a list of xxx with two values: name, unitGuid"""
        response_json = self.get_api("units")
        return [] if response_json is None else response_json["units"]

    def values(self, unit_guid: str, value_guids=None):
        """Get Genset values"""
        if value_guids is None:
            response_json = self.get_api("values", unit_guid=unit_guid)
        else:
            response_json = self.get_api(
                "values", unit_guid, {"valueGuids": value_guids}
            )
        values = [] if response_json is None else response_json["values"]
        for value in values:
            value["timeStamp"] = timestring.Date(value["timeStamp"]).date
        return values

    def info(self, unit_guid):
        """Get Genset info"""
        response_json = self.get_api("info", unit_guid=unit_guid)
        return [] if response_json is None else response_json

    def comments(self, unit_guid):
        """Get Genset comments"""
        response_json = self.get_api("comments", unit_guid=unit_guid)
        comments = [] if response_json is None else response_json["comments"]
        for comment in comments:
            comment["date"] = timestring.Date(comment["date"]).date
        return comments

    def history(self, unit_guid, _from=None, _to=None, value_guids=None):
        """Get Genset history"""
        payload = {}
        if _from is not None:
            payload["from"] = _from
        if _to is not None:
            payload["to"] = _to
        if value_guids is not None:
            payload["valueGuids"] = value_guids
        response_json = self.get_api("history", unit_guid=unit_guid, payload=payload)
        values = [] if response_json is None else response_json["values"]
        for value in values:
            for entry in value["history"]:
                entry["validTo"] = timestring.Date(entry["validTo"]).date
        return values

    def files(self, unit_guid):
        """Get Genset files"""
        response_json = self.get_api("files", unit_guid=unit_guid)
        files = [] if response_json is None else response_json["files"]
        for file in files:
            file["generated"] = timestring.Date(file["generated"]).date
        return files

    def download(self, unit_guid, file_name, path=""):
        """Download a file with 'file_name', store it in the 'path'"""
        try:
            _url = WSV_URL["download"].format(self.__login_id, unit_guid, file_name)
            body = {}
            try:
                response = requests.get(
                    _url, headers=self._headers, params=body, timeout=TIMEOUT
                )
            except requests.exceptions.Timeout:
                _LOGGER.error("API get 'download' response time-out.")
                return False
            _LOGGER.debug("Calling API url %s", response.url)
            if response.status_code != 200:
                _LOGGER.error(
                    "API 'download' returned code: " "%s (%s) ",
                    response.status_code,
                    response.reason,
                )
                return False
        except Exception as e:
            _LOGGER.error("API 'download' error %s", e)
            return False
        try:
            with open(os.path.join(path, file_name), "wb") as f:
                f.write(response.content)
            f.close()
        except Exception as e:
            _LOGGER.error(f"API 'download' error {e}")
            return False
        return True

    def command(self, unit_guid: str, command: str, mode=None):
        "Send a command"

        body = {"command": command}
        if mode is not None:
            body["mode"] = mode
        return self.post_api("command", unit_guid=unit_guid, payload=body)

    def get_unit_guid(self, name):
        """Find GUID for unit name"""
        unit = next(
            (unit for unit in self.units() if unit["name"].find(name) >= 0), None
        )
        return None if unit is None else unit["unitGuid"]

    def get_value_guid(self, unit_guid, name):
        """Find guid of a value"""
        value = next(
            (
                value
                for value in self.values(unit_guid)
                if value["name"].find(name) >= 0
            ),
            None,
        )
        return None if value is None else value["valueGuid"]
