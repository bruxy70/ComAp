"""comap.api_async module

A wrapper around ComAp API, that allows easy automation of WebSupervisor tasks, such as downloading and analyzing data.
The instructions for testing and examples are available on ComAp-API repository.

There are two modules available - a simpler synchronous module `comap.api` and asynchronous module `comap.api_async`. The async module is recommended for use in production.

This module contains two classes:

- Identity  - serves to authenticate to ComAp Cloud and obtain the token
              used in the individual APIs.
- WSV       - set of APIs to communicate with the WebSupervisor PRO

"""
import asyncio
import logging
import os
from datetime import datetime

import aiofiles
import aiohttp
import async_timeout

from .constants import AUTHORIZATION, COMAP_KEY, IDENTITY_URL, TIMEOUT, WSV_URL

_LOGGER = logging.getLogger(__name__)


class ErrorGettingData(Exception):
    """Raised when we cannot get data from API"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ComApCloud:
    """The base class for both APIs"""

    def __init__(
        self, session: aiohttp.ClientSession, headers: dict, login_id: str = None
    ) -> None:
        """Create ComAp Cloud API instance

        Parameters:
        -----------
        session: `aiohttp.ClientSession`
            HTTPS connection pool instance
        headers: `dict`
            Contain ComAp Key, and for WSV API Authorization (Bearer token)
        login_id: `str`, optional
            the user name (each identity can have multiple user names)
        """
        self._headers = headers
        self._session = session
        self._login_id = login_id

    async def get_api(
        self,
        application: dict,
        api: str,
        unit_guid: str | None = None,
        file_name: str | None = None,
        payload: dict | None = None,
    ) -> aiohttp.ClientResponse | None:
        """Call ComAp GET API.

        Parameters:
        -----------
        application: `dict`
            points to dictionary of URLs for different APIs
        api: `str`
            one of the keys in the application dictionary
        unit_guid: `str`, optional
            for WSV API - the genset ID (from the `units` API, or in WSV application front-end)
        file_name: `str`, optional
            for WSV download API - file name
        payload: `dict`, optional
            some APIs require a payload

        Returns:
        --------
        `aiohttp.ClientResponse` or `None` if not succesfull
        """
        if api not in application:
            _LOGGER.error("Unknown API '%s'!", api)
            return None
        _url = application[api].format(
            login_id=self._login_id, unit_guid=unit_guid, file_name=file_name
        )
        _body = {} if payload is None else payload
        try:
            with async_timeout.timeout(TIMEOUT):
                response = await self._session.get(
                    _url, headers=self._headers, params=_body
                )
            if response.status != 200:
                response_text = await response.text()
                _LOGGER.error(
                    "API GET '%s' returned code: %s (%s)",
                    api,
                    response.status,
                    response_text,
                )
                return None
        except asyncio.TimeoutError:
            _LOGGER.error("API GET '%s' response timeout", api)
            return None
        except Exception as e:
            _LOGGER.error(f"API GET '%s' error %s", api, e)
            return None
        return response

    async def post_api(
        self,
        application: dict,
        api: str,
        unit_guid: str | None = None,
        payload: dict | None = None,
    ) -> aiohttp.ClientResponse | None:
        """Call ComAp POST API.

        Parameters:
        -----------
        application: `dict`
            points to dictionary of URLs for different APIs
        api: `str`
            one of the keys in the application dictionary
        unit_guid: `str`, optional
            for WSV API - the genset ID (from the `units` API, or in WSV application front-end)
        payload: `dict`, optional
            some APIs require a payload

        Returns:
        --------
        `aiohttp.ClientResponse` or `None` if not succesfull
        """
        if api not in application:
            _LOGGER.error("Unknown API '%s'!", api)
            return None
        _url = application[api].format(login_id=self._login_id, unit_guid=unit_guid)
        _body = {} if payload is None else payload
        try:
            with async_timeout.timeout(TIMEOUT):
                response = await self._session.post(
                    _url, headers=self._headers, json=_body
                )
            if response.status != 200:
                response_text = await response.text()
                _LOGGER.error(
                    "API POST '%s' returned code: %s (%s)",
                    api,
                    response.status,
                    response_text,
                )
                return None
        except asyncio.TimeoutError:
            _LOGGER.error("API POST '%s' response timeout", api)
            return None
        except Exception as e:
            _LOGGER.error("API POST '%s' error %s", api, e)
            return None
        return response


class Identity(ComApCloud):
    """ComAp Cloud Identity API wrapper"""

    def __init__(self, session: aiohttp.ClientSession, key: str) -> None:
        """Setup of the ComAp Cloud Identity API class

        Parameters:
        ----------
        session: `aiohttp.ClientSession`
            HTTPS connection pool instance
        key: `str`
            ComAp Key (from the API profile)
        """
        super().__init__(
            session=session,
            headers={"Content-Type": "application/json", COMAP_KEY: key},
        )

    async def authenticate(self, client_id: str, secret: str) -> dict | None:
        """Authenticate and return bearer token dictionary.

        Parameters:
        -----------
        client_id: `str`
            From ComAp customer portal
            Or generated on API Documentation test portal using Create application registration API
        secret: `str`
            From ComAp customer portal
            Or generated on API Documentation test portal using Create application secret API

        Returns:
        --------
        The bearer access token `dict` or `None` if failed.
        {
            'token_type': `str`,
            'expires_in': `number`,
            'ext_expires_in': `number`,
            'access_token': `str` # this is the Bearer access token
        }
        """
        body = {"clientId": client_id, "secret": secret}
        response = await self.post_api(
            application=IDENTITY_URL, api="authenticate", payload=body
        )
        return None if response is None else await response.json()


class WSV(ComApCloud):
    """ComAp Cloud WSV API wrapper"""

    def __init__(
        self, session: aiohttp.ClientSession, login_id: str, key: str, token: str
    ) -> None:
        """Setup of the ComAp Cloud WSV API class

        Parameters:
        -----------
        session: `aiohttp.ClientSession`
            HTTPS connection pool instance
        login_id: `str`
            the user name (each identity can have multiple user names)
        key: `str`
            ComAp Key (from the API profile)
        token: `str`
            The Bearer token received from Identity API authenticate
        """
        super().__init__(
            session=session,
            headers={
                "Content-Type": "application/json",
                COMAP_KEY: key,
                AUTHORIZATION: "Bearer " + token,
            },
            login_id=login_id,
        )

    async def units(self) -> list:
        """Get list of all units

        Returns:
        --------
        `list` of `dict`
        [{
            'name': `str`,
            'unitGuid': `str`,
            'url': `str`
        }]
        """
        response = await self.get_api(application=WSV_URL, api="units")
        response_json = {"units":[]} if response is None else await response.json()
        return response_json["units"]

    async def values(
        self, unit_guid: str, value_guids: str | None = None
    ) -> list:
        """Get Genset values

        Parameters:
        -----------
        unit_guid: str
            the genset ID (from the `units` API, or in WSV application front-end)
        value_guids: str, optional
            list of the value guids separated by comma
            (get it by calling this function with no parameter or `get_value_guid`)

        Returns:
        --------
        `list` of `dict`:
        [{
            'name': `str`,
            'valueGuid': `str`,
            'value': `str`,
            'unit': `str`,
            'highLimit': `number`,
            'lowLimit': `number`,
            'decimalPlaces': `number`,
            'timeStamp': `datetime`
        }]
        """
        if value_guids is None:
            response = await self.get_api(
                application=WSV_URL, api="values", unit_guid=unit_guid
            )
        else:
            response = await self.get_api(
                application=WSV_URL,
                api="values",
                unit_guid=unit_guid,
                payload={"valueGuids": value_guids},
            )
        response_json = {"values":[]} if response is None else await response.json()
        values = response_json["values"]
        for value in values:
            value["timeStamp"] = datetime.fromisoformat(value["timeStamp"])
        return values

    async def info(self, unit_guid: str) -> dict:
        """Get Genset info

        Parameters:
        -----------
        unit_guid: str
            the genset ID (from the `units` API, or in WSV application front-end)

        Returns:
        --------
        Genset info:
        {'name': `str`,
        'unitGuid': `str`,
        'ownerLoginId': `str`,
        'applicationType': `str`,
        'timezone': '`str`,
        'connection': {
            'enabled': `boolean`,
            'airGateId': `str`,
            'ipAddress': `str`,
            'port': `number`,
            'controllerAddress': `number`
        },
        'position': {
            'positionType': `str`,
            'latitude': `number`,
            'longitude': `number`}
        }
        """
        response = await self.get_api(
            application=WSV_URL, api="info", unit_guid=unit_guid
        )
        return {} if response is None else await response.json()

    async def comments(self, unit_guid: str) -> list:
        """Get Genset comments

        Parameters:
        -----------
        unit_guid: str
            the genset ID (from the `units` API, or in WSV application front-end)

        Returns:
        --------
        `list` of `dict`
        [{
            "id": `number`,
            "auhtor": `str`,
            "date": `datetime`,
            "text": `str`,
            "active": `Boolean`
        }]
        """
        response = await self.get_api(
            application=WSV_URL, api="comments", unit_guid=unit_guid
        )
        response_json = {"comments":[]} if response is None else await response.json()
        comments = response_json["comments"]
        for comment in comments:
            comment["date"] = datetime.fromisoformat(comment["date"])
        return comments

    async def history(
        self,
        unit_guid: str,
        _from: str | None = None,
        _to: str | None = None,
        value_guids: str | None = None,
    ) -> list:
        """Get Genset history

        Parameters:
        -----------
        unit_guid: str
            the genset ID (from the `units` API, or in WSV application front-end)
        _from: `str` in format 'MM/DD/YYYY', optional
            history start date
        _to: `str` in format 'MM/DD/YYYY', optional
            history end date
        value_guids: `list`, optional
            list of the value guids separated by comma
            (get it by calling `values` or `get_value_guid`)

        Returns:
        --------
        `list` of `dict`
        [{
            'value': `str`,
            'validFrom': `datetime`,
            'validTo': `datetime`
        }]
        """
        payload = {}
        if _from is not None:
            payload["from"] = _from
        if _to is not None:
            payload["to"] = _to
        if value_guids is not None:
            payload["valueGuids"] = value_guids
        response = await self.get_api(
            application=WSV_URL, api="history", unit_guid=unit_guid, payload=payload
        )
        response_json = {"values":[]} if response is None else await response.json()
        values = response_json["values"]
        for value in values:
            for entry in value["history"]:
                entry["validFrom"] = datetime.fromisoformat(entry["validFrom"])
                entry["validTo"] = datetime.fromisoformat(entry["validTo"])
        return values

    async def files(self, unit_guid: str) -> list:
        """Get Genset files

        Parameters:
        -----------
        unit_guid: str
            the genset ID (from the `units` API, or in WSV application front-end)

        Returns:
        --------
        `list` of `dict`:
        [{
            'fileName': `str`,
            'fileType': `str`,
            'generated': `datetime`
        }]
        """
        response = await self.get_api(
            application=WSV_URL, api="files", unit_guid=unit_guid
        )
        response_json = {"files":[]} if response is None else await response.json()
        files = response_json["files"]
        for file in files:
            file["generated"] = datetime.fromisoformat(file["generated"])
        return files

    async def download(
        self, unit_guid: str, file_name: str, path: str = ""
    ) -> bool:
        """Download a file with 'file_name', store it in the 'path'

        Parameters:
        -----------
        unit_guid: str
            the genset ID (from the `units` API, or in WSV application front-end)
        file_name: str
            List names by calling `files`
        path: str, optional
            Local directory to save the file (current directory if not specified)

        Returns:
        --------
        `bool`: Was the download succesful?
        """

        response = await self.get_api(
            application=WSV_URL,
            api="download",
            unit_guid=unit_guid,
            file_name=file_name,
        )
        if response is None:
            return False
        try:
            f = await aiofiles.open(os.path.join(path, file_name), mode="wb")
            await f.write(await response.read())
            await f.close()
        except Exception as e:
            _LOGGER.error(f"API 'download' error {e}")
            return False
        return True

    async def command(
        self, unit_guid: str, command: str, mode: str | None = None
    ) -> dict:
        """Send a command

        Parameters:
        -----------
        unit_guid: str
            the genset ID (from the `units` API, or in WSV application front-end)
        command: str
            see the API documentation
        mode: str, optional
            see the API documentation

        Returns:
        --------
        `dict`: json return value
        """

        body = {"command": command}
        if mode is not None:
            body["mode"] = mode
        response = await self.post_api(
            application=WSV_URL, api="command", unit_guid=unit_guid, payload=body
        )
        return {} if response is None else await response.json()

    async def get_unit_guid(self, name: str) -> str | None:
        """Call units API and find GUID for a unit by name

        Parameters:
        -----------
        name: str
            Name of the unit

        Returns:
        --------
        unitGuid (`str`) or `None`
        """
        unit = next(
            (unit for unit in await self.units() if unit["name"].find(name) >= 0),
            None,
        )
        return None if unit is None else unit["unitGuid"]

    async def get_value_guid(self, unit_guid: str, name: str) -> str | None:
        """Call values API and find GUID for a value by name

        Parameters:
        -----------
        unit_guid: str
            the genset ID (from the `units` API, or in WSV application front-end)
        name: str
            Name of the value

        Returns:
        --------
        valueGuid (`str`) or `None`

        """
        value = next(
            (
                value
                for value in await self.values(unit_guid)
                if value["name"].find(name) >= 0
            ),
            None,
        )
        return None if value is None else value["valueGuid"]
