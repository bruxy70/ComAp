"""
comap.api_async module
"""
import asyncio
import logging
import os

import aiofiles
import async_timeout
import timestring

from .constants import AUTHORIZATION, COMAP_KEY, IDENTITY_URL, TIMEOUT, WSV_URL

_LOGGER = logging.getLogger(__name__)


class ErrorGettingData(Exception):
    """Raised when we cannot get data from API"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ComApCloudAsync:
    """Create ComAp Cloud API instance"""

    def __init__(self, headers: dict, session) -> None:
        """Create ComAp Cloud API instance"""
        self._headers = headers
        self._session = session

    async def _async_get_api(
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

            with async_timeout.timeout(TIMEOUT):
                response = await self._session.get(
                    _url, headers=self._headers, params=body
                )
            if response.status != 200:
                response_text = await response.text()
                _LOGGER.error(
                    f"API {api} returned code: "
                    f"{response.status} "
                    f"({response_text})"
                )
                return None
        except asyncio.TimeoutError:
            _LOGGER.error("API %s response timeout", api)
            return None
        except Exception as e:
            _LOGGER.error(f"API %s error %s", api, e)
            return None
        return await response.json()

    async def _async_post_api(
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

            with async_timeout.timeout(TIMEOUT):
                response = await self._session.post(
                    _url, headers=self._headers, params=body
                )
            if response.status != 200:
                response_text = await response.text()
                _LOGGER.error(
                    f"API {api} returned code: "
                    f"{response.status} "
                    f"({response_text})"
                )
                return None
        except asyncio.TimeoutError:
            _LOGGER.error("API %s response timeout", api)
            return None
        except Exception as e:
            _LOGGER.error(f"API %s error %s", api, e)
            return None
        return await response.json()


class IdentityAsync(ComApCloudAsync):
    """Create ComAp Cloud Identity API instance"""

    def __init__(self, key: str, session) -> None:
        """Setup of the ComAp Cloud Identity API class"""
        super().__init__({"Content-Type": "application/json", COMAP_KEY: key}, session)

    async def async_get_api(self, api: str, payload: dict = None) -> str | dict:
        """Call ComAp Identity get API. Return response JSON if succesfull, None if not succesfull"""
        response = await self._async_get_api(
            application=IDENTITY_URL, api=api, payload=payload
        )
        return None if response is None else response

    async def async_post_api(self, api: str, payload: dict = None) -> str | dict:
        """Call ComAp Identity post API. Return response JSON if succesfull, None if not succesfull"""
        response = await self._async_post_api(
            application=IDENTITY_URL, api=api, payload=payload
        )
        return None if response is None else response

    async def async_authenticate(self, client_id: str, secret: str) -> dict | None:
        """Authenticate and return bearer token dictinary. The token is in ['access_token']"""
        body = {"clientId": client_id, "secret": secret}
        return await self.async_post_api(api="authenticate", payload=body)


class WSV_Async(ComApCloudAsync):
    """Constructor"""

    def __init__(self, session, login_id: str, key: str, token: str) -> None:
        """Setup of the czpubtran library"""
        self.__login_id = login_id
        super().__init__(
            {
                "Content-Type": "application/json",
                COMAP_KEY: key,
                AUTHORIZATION: "Bearer " + token,
            },
            session,
        )

    async def async_get_api(
        self,
        api: str,
        unit_guid: str | None = None,
        payload: dict = None,
    ) -> dict | None:
        """Call ComAp Identity get API. Return response JSON if succesfull, None if not succesfull"""
        response = await self._async_get_api(
            application=WSV_URL,
            api=api,
            login_id=self.__login_id,
            unit_guid=unit_guid,
            payload=payload,
        )
        return None if response is None else response

    async def async_post_api(
        self, api: str, unit_guid: str | None = None, payload: dict = None
    ) -> dict | None:
        """Call ComAp Identity post API. Return response JSON if succesfull, None if not succesfull"""
        response = await self._async_post_api(
            application=IDENTITY_URL,
            api=api,
            login_id=self.__login_id,
            unit_guid=unit_guid,
            payload=payload,
        )
        return None if response is None else response

    async def async_units(self):
        """Get list of all units - returns a list of xxx with two values: name, unitGuid"""
        response_json = await self.async_get_api("units")
        return [] if response_json is None else response_json["units"]

    async def async_values(self, unit_guid, value_guids=None):
        """Get Genset values"""
        if value_guids is None:
            response_json = await self.async_get_api("values", unit_guid)
        else:
            response_json = await self.async_get_api(
                "values", unit_guid, {"valueGuids": value_guids}
            )
        values = [] if response_json is None else response_json["values"]
        for value in values:
            value["timeStamp"] = timestring.Date(value["timeStamp"]).date
        return values

    async def comments(self, unit_guid):
        """Get Genset comments"""
        response_json = await self.async_get_api("comments", unit_guid)
        comments = [] if response_json is None else response_json["comments"]
        for comment in comments:
            comment["date"] = timestring.Date(comment["date"]).date
        return comments

    async def async_info(self, unit_guid):
        """Get Genset info"""
        response_json = await self.async_get_api("info", unit_guid)
        return [] if response_json is None else response_json

    async def async_comments(self, unit_guid):
        """Get Genset comments"""
        response_json = await self.async_get_api("comments", unit_guid)
        comments = [] if response_json is None else response_json["comments"]
        for comment in comments:
            comment["date"] = timestring.Date(comment["date"]).date
        return comments

    async def async_history(self, unit_guid, _from=None, _to=None, value_guids=None):
        """Get Genset history"""
        payload = {}
        if _from is not None:
            payload["from"] = _from
        if _to is not None:
            payload["to"] = _to
        if value_guids is not None:
            payload["valueGuids"] = value_guids
        response_json = await self.async_get_api("history", unit_guid, payload)
        values = [] if response_json is None else response_json["values"]
        for value in values:
            for entry in value["history"]:
                entry["validTo"] = timestring.Date(entry["validTo"]).date
        return values

    async def async_files(self, unit_guid):
        """Get Genset files"""
        response_json = await self.async_get_api("files", unit_guid)
        files = [] if response_json is None else response_json["files"]
        for file in files:
            file["generated"] = timestring.Date(file["generated"]).date
        return files

    async def async_download(self, unit_guid, file_name, path=""):
        "download file"
        _url = WSV_URL["download"].format(self.__login_id, unit_guid, file_name)
        try:
            with async_timeout.timeout(TIMEOUT):
                response = await self._session.get(_url, headers=self._headers)
            if response.status != 200:
                response_text = await response.text()
                _LOGGER.error(
                    f"API {api} returned code: "
                    f"{response.status} "
                    f"({response_text})"
                )
                return None
            f = await aiofiles.open(os.path.join(path, file_name), mode="wb")
            await f.write(await response.read())
            await f.close()
            return True
        except asyncio.TimeoutError:
            _LOGGER.error(f"API {api} response timeout")
            return False
        except Exception as e:
            _LOGGER.error(f"API {api} error {e}")
            return False

    async def async_command(self, unit_guid, command, mode=None):
        "send command"

        body = {"command": command}
        if mode is not None:
            body["mode"] = mode
        return await self.async_get_api("command", unit_guid, body)

    async def async_get_unit_guid(self, name):
        """Find GUID for unit name"""
        unit = next(
            (unit for unit in await self.async_units() if unit["name"].find(name) >= 0),
            None,
        )
        return None if unit is None else unit["unitGuid"]

    async def async_get_value_guid(self, unitGuid, name):
        """Find guid of a value"""
        value = next(
            (
                value
                for value in await self.async_values(unitGuid)
                if value["name"].find(name) >= 0
            ),
            None,
        )
        return None if value is None else value["valueGuid"]
