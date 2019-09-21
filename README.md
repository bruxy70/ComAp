# ComAp API
Allows easy automation of [WebSupervisor](https://www.websupervisor.net/) tasks, such as downloading and analyzing data.

The instruction for testing and examples are available on [ComAp-API repository](https://github.com/bruxy70/ComAp-API)

# Documentation
The modules provide easy access to the ComAp API. For more detail about the retuned values, check the [ComAp API Developer Portal](https://websupervisor.portal.azure-api.net/docs/services)

There are two modules available - a simpler synchronos module `comap.api` and asynchronous module `comap.api_async`. The async module is recommended for use in production.
For better understanding, please look at the examples on the [ComAp-API repository](https://github.com/bruxy70/ComAp-API)

## comap.api
### Class: wsv(key, token='')
Use the API ``ComAp-Key`` and ``Token`` to inicialize the object. Example:
```python
from comap.api import wsv
# Do not store your API secrets in code, but in an external file
from config import ComAp-Key, Token

wsv = wsv(ComAp-Key, Token)
units = wsv.units()
for unit in units:
    print(f'{unit["unitGuid"]} : {unit["name"]}')
```

### Methods
#### authenticate(username, password)
Get the authentication `Token`. 
Example:
```python
from comap.api import wsv
from config import ComAp-Key
username=input('Enter username:')
password=input('Enter password:')
token=wsv(ComAp-Key).authenticate(username, password)
print("Your token is:", token)
```

#### units()
Get list of units with their unitGuid - for more examples, look on the [ComAp-API repository](https://github.com/bruxy70/ComAp-API)

#### values(unitGuid, valueGuids=None)
Get list of values. It is recommended to specify comma separated list of valueGuids to filter the result
You can import VALUE_GUID from comap.constants to get GUIDs for the most common values. Or call the method without GUID to get all values available in teh controller, including their GUIDs.

#### info(unitGuid)
Get information about the unit

#### comments(unitGuid)
Get comments entered in the WebSupervisor (these can be used for maintenance tasks)

#### history(unitGuid, _from=None, _to=None, valueGuids=None)
Get history of a value. Please specify the valueGuid and `from` and `to` dates in the format `"MM/DD/YYYY"`

#### files(unitGuid)
Get list of files stored on the controller

#### download(unitGuid, fileName, path='')
Download a file from the controller to the current directory (or the directory specified in `path`). You can list the files using the `files` method.

#### command(unitGuid, command, mode=None)
This allows to control the genset. The available commands are `start`,`stop`,`faultReset`,`changeMcb` (toggle mains circuit breaker), `changeGcb` (toggle genset circuit breaker) and `changeMode`. 
For `changeMode` enter the `mode` parameter e.g. to `man` or `auto`

#### get_unit_guid(name)
Find a genset by name. Return is unitGuid

#### get_value_guid(unitGuid, name)
Find a value by name. Return valueGuid

---

## comap.api_async methods
### Class: wsv_async(key, token='')
Use the API ``ComAp-Key`` and ``Token`` to inicialize the object

### Methods
Same as comap.api, but each method starting with `async_`, and include a session parameter (for example `async_units(session)`, or `values(session,unitGuid,valueGuids=None)`
Rather than explaing it - see the difference in the [async example](https://github.com/bruxy70/ComAp-API/tree/development/simple-examples-async)