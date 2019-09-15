"""
comapapi library

async_units() - list all units
async_get_unit_guid(name) - find unit with name
async_unit_values(unitGuid,valueGuids=None) - return genset value (or values)
async_get_unit_value_guid(unitGuid,name) - find value with name

"""
import logging, json
from datetime import datetime, date, time, timedelta
import asyncio
import aiohttp
import async_timeout
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

class comapapi():
    
    """Constructor"""
    def __init__(self, session,key,token):
        """Setup of the czpubtran library"""
        self._load_defaults()
        self._api_key = key
        self._api_token = token
        self._session = session
    
    def _load_defaults(self):
        """Erase the information"""

    async def _async_call_api(self,api,unitGuid=None,payload={}):
        """Call ComAp API. Return None if not succesfull"""
        if self._api_key is None or self._api_token is None:
            _LOGGER.error( f'API Token and Comap-Key not available!')
            return None
        if api not in URL:
            _LOGGER.error( f'Unknown API {api}!')
            return None
        headers = {'Token':self._api_token,'Comap-Key': self._api_key}
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
            response_json = await self._async_call_api('values')
        else:
            response_json = await self._async_call_api('values',{'valueGuids':valueGuids})
        return [] if response_json is None else response_json['values']

    async def async_info(self,unitGuid):
        """Get Genset values"""
        response_json = await self._async_call_api('info',unitGuid)
        return [] if response_json is None else response_json

    async def async_history(self,unitGuid,_from=None,_to=None,valueGuids=None):
        """Get Genset history"""
        payload={}
        if _from is not None: payload['from'] = _from
        if _to is not None: payload['to'] = _to
        if valueGuids is not None: payload['valueGuids'] = valueGuids 
        response_json = await self._async_call_api('history',unitGuid,payload)
        return [] if response_json is None else response_json['values']

    async def async_files(self,unitGuid):
        """Get Genset files"""
        response_json = await self._async_call_api('files',unitGuid)
        return [] if response_json is None else response_json['files']

    async def async_get_unit_guid(self,name):
        """Find GUID for unit name"""
        unit=list(filter(lambda u: u['name']==name,await self.async_units()))
        return None if len(unit)==0 else unit[0]['unitGuid']

    async def async_get_value_guid(self,unitGuid,name):
        """Find guid of a value"""
        values=list(filter(lambda v: v['name']==name,await self.async_values(unitGuid)))
        return None if len(values)==0 else values[0]['valueGuid']

    async def async_download(self,unitGuid,fileName,path=None):
        "download file"
        if self._api_key is None or self._api_token is None:
            _LOGGER.error( f'API Token and Comap-Key not available!')
            return False
        headers = {'Token':self._api_token,'Comap-Key': self._api_key}
        try:
            api='download'
            _url= URL[api].format(unitGuid,fileName)
            with async_timeout.timeout(HTTP_TIMEOUT):            
                response = await self._session.get(_url,headers=headers)
            if response.status!= 200:
                _LOGGER.error( f'API {api} returned code: {response.code} ({response.status}) ')    
                return False
            with open(fileName if path is None else f'{path}/{fileName}', 'wb') as f:
                f.write(response.content)
        except (asyncio.TimeoutError):
            _LOGGER.error( f'API {api} response timeout')
            return False
        except Exception as e:
            _LOGGER.error( f'API {api} error {e}')
            return False

        
    async def async_authenticate(self):
        return

    """Properties"""
