"""
comap.api_async module
"""
import logging, json
import os
import aiofiles
from datetime import datetime, date, time, timedelta
import asyncio
import aiohttp
import async_timeout
import timestring
from .constants import URL

HTTP_TIMEOUT = 10
API_KEY = 'Comap-Key'
API_TOKEN = 'Token'

_LOGGER = logging.getLogger(__name__)

class ErrorGettingData(Exception):
    """Raised when we cannot get data from API"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class wsv_async():
    """Constructor"""
    def __init__(self, session,key,token=''):
        """Setup of the czpubtran library"""
        self._api_key = key
        self._api_token = token
        self._session = session
    
    async def _async_call_api(self,api,unitGuid=None,payload={}):
        """Call ComAp API. Return None if not succesfull"""
        if self._api_key is None or self._api_token is None:
            _LOGGER.error( f'API Token and Comap-Key not available!')
            return None
        if api not in URL:
            _LOGGER.error( f'Unknown API {api}!')
            return None
        headers = {API_TOKEN:self._api_token,API_KEY: self._api_key}
        try:
            _url= URL[api] if unitGuid is None else URL[api].format(unitGuid)
            with async_timeout.timeout(HTTP_TIMEOUT):            
                response = await self._session.get(_url,headers=headers,params=payload)
            if response.status!= 200:
                _LOGGER.error( f'API {api} returned code: {response.code} ({response.status}) ')    
                return None
        except (asyncio.TimeoutError):
            _LOGGER.error( f'API {api} response timeout')
            return None
        except Exception as e:
            _LOGGER.error( f'API {api} error {e}')
            return None
        return await response.json()

    async def async_units(self):
        """Get list of all units - returns a list of xxx with two values: name,unitGuid"""
        response_json = await self._async_call_api('units')
        return [] if response_json is None else response_json['units']

    async def async_values(self,unitGuid,valueGuids=None):
        """Get Genset values"""
        if valueGuids==None:
            response_json = await self._async_call_api('values',unitGuid)
        else:
            response_json = await self._async_call_api('values',unitGuid,{'valueGuids':valueGuids})
        values = [] if response_json is None else response_json['values']
        for value in values:
            value["timeStamp"]=timestring.Date(value["timeStamp"]).date
        return values

    async def comments(self,unitGuid):
        """Get Genset comments"""
        response_json = await self._async_call_api('comments',unitGuid)
        comments = [] if response_json is None else response_json['comments']
        for comment in comments:
            comment["date"]=timestring.Date(comment["date"]).date
        return comments

    async def async_info(self,unitGuid):
        """Get Genset info"""
        response_json = await self._async_call_api('info',unitGuid)
        return [] if response_json is None else response_json

    async def async_history(self,unitGuid,_from=None,_to=None,valueGuids=None):
        """Get Genset history"""
        payload={}
        if _from is not None: payload['from'] = _from
        if _to is not None: payload['to'] = _to
        if valueGuids is not None: payload['valueGuids'] = valueGuids 
        response_json = await self._async_call_api('history',unitGuid,payload)
        values = [] if response_json is None else response_json['values']
        for value in values:
            for entry in value["history"]:
                entry["validTo"]=timestring.Date(entry["validTo"]).date
        return values

    async def async_files(self,unitGuid):
        """Get Genset files"""
        response_json = await self._async_call_api('files',unitGuid)
        files=[] if response_json is None else response_json['files']
        for file in files:
            file["generated"]=timestring.Date(file["generated"]).date
        return files

    async def async_authenticate(self,username,password):
        """Get Authentication Token"""
        if self._api_key is None:
            _LOGGER.error( f'API Comap-Key not available!')
            return None
        api="authenticate"
        headers = {API_KEY: self._api_key,'Content-Type':'application/json'}
        body={'username':username,'password':password}
        try:
            _url= URL[api]
            with async_timeout.timeout(HTTP_TIMEOUT):            
                response = await self._session.post(_url,headers=headers,json=body)
            if response.status!= 200:
                _LOGGER.error( f'API {api} returned code: {response.code} ({response.status}) ')    
                return None
        except (asyncio.TimeoutError):
            _LOGGER.error( f'API {api} response timeout')
            return None
        except Exception as e:
            _LOGGER.error( f'API {api} error {e}')
            return None
        response_json = await response.json()
        self._api_token = '' if response_json is None else response_json['applicationToken']
        return self._api_token

    async def async_download(self,unitGuid,fileName,path=''):
        "download file"
        if self._api_key is None or self._api_token is None:
            _LOGGER.error( f'API Token and Comap-Key not available!')
            return False
        headers = {API_TOKEN:self._api_token,API_KEY: self._api_key}
        try:
            api='download'
            _url= URL[api].format(unitGuid,fileName)
            with async_timeout.timeout(HTTP_TIMEOUT):            
                response = await self._session.get(_url,headers=headers)
            if response.status!= 200:
                _LOGGER.error( f'API {api} returned code: {response.code} ({response.status}) ')    
                return False
            f = await aiofiles.open(os.path.join(path,fileName), mode='wb')
            await f.write(await response.read())
            await f.close()            
            return True
        except (asyncio.TimeoutError):
            _LOGGER.error( f'API {api} response timeout')
            return False
        except Exception as e:
            _LOGGER.error( f'API {api} error {e}')
            return False

    async def async_command(self,unitGuid,command,mode=None):
        "send command"
        if self._api_key is None or self._api_token is None:
            _LOGGER.error( f'API Token and Comap-Key not available!')
            return False
        headers = {API_TOKEN:self._api_token,API_KEY: self._api_key,'Content-Type':'application/json'}
        body={'command':command}
        if command=='mode': body['mode']=mode
        try:
            api='command'
            _url= URL[api].format(unitGuid)
            with async_timeout.timeout(HTTP_TIMEOUT):            
                response = await self._session.post(_url,headers=headers,json=body)
            if response.status_code!= 200:
                _LOGGER.error( f'API {api} returned code: {response.status_code} ({response.reason}) ')    
                return False
            _LOGGER.debug( f'Calling API url {response.url}')
        except (asyncio.TimeoutError):
            _LOGGER.error( f'API {api} response timeout')
            return False
        except Exception as e:
            _LOGGER.error( f'API {api} error {e}')
            return False
        return True

    async def async_get_unit_guid(self,name):
        """Find GUID for unit name"""
        unit = next((unit for unit in await self.async_units() if unit['name'].find(name)>=0),None)
        return None if unit==None else unit['unitGuid']

    async def async_get_value_guid(self,unitGuid,name):
        """Find guid of a value"""
        value = next((value for value in await self.async_values(unitGuid) if value['name'].find(name)>=0),None)
        return None if value==None else value['valueGuid']