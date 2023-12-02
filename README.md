This is a wrapper around ComAp API, that allows easy automation of [WebSupervisor](https://www.websupervisor.net/) tasks, such as downloading and analyzing data.
The instructions for testing and examples are available on [ComAp-API repository](https://github.com/bruxy70/ComAp-API)

There are two modules available:

- a simpler synchronous module [`comap.api`](#comapapi)
- and asynchronous module [`comap.api_async`](#comapapi_async)

The async module is recommended for use in production.

The modules provide easy access to the ComAp API. For more details about the returned values, check the [ComAp API Developer Portal](https://websupervisor.portal.azure-api.net/docs/services)

For a better understanding, look at the examples on the [ComAp-API repository](https://github.com/bruxy70/ComAp-API)

# comap.api

This module contains two classes:

- [Identity](#class-identitykey-str) - serves to authenticate to ComAp Cloud and obtain the token
             used in the individual APIs.
- [WSV](#class-wsvlogin_idstr-keystr-tokenstr) - set of APIs to communicate with the WebSupervisor PRO

---

## Class: Identity(key: str)

Use `ComAp-Key`, `client_id` and `secret` to obtain the ``Bearer Token``, that is needed to authenticate to the WSV API.

*Example:*

```python
from comap import api

CLIENT_ID = ... # get the id from the a repository
SECRET = ...    # get the secret from a key repository
COMAP_KEY = ... # get the key from a key repository

# Use the ComAp Cloud Identity API to get the Bearer token
identity = api.Identity(COMAP_KEY)
token = identity.authenticate(CLIENT_ID, SECRET)
```

*Returns*

```yaml
{
    'token_type': 'Bearer',
    'expires_in': 3599,
    'ext_expires_in': 3599,
    'access_token': 'eyJ0e***redacted***1Z_roeA'
}
```

Get the `ComAp-Key` in your [Profile](https://portal.websupervisor.net/developer), the other two values will be available on the Customer portal.

Until then, you can generate them from the API documentation using the "Try it" feature:

1. [Create Application Registration](https://portal.websupervisor.net/docs/services/comap-cloud-identity/operations/application-create?) - this will return the `client_id`.
2. [Create Application Secret](https://portal.websupervisor.net/docs/services/comap-cloud-identity/operations/application-secret-create?) - this will return the secret

These values are valid for 2 years. If you need new values, [Delete Application Registration](https://portal.websupervisor.net/docs/services/comap-cloud-identity/operations/application-delete?) and create new ones.

### authenticate(self, client_id: str, secret: str) ‑> dict | None

Authenticate and return bearer token dictionary.

| Parameter | Type | Value |
| --- | --- | --- |
| client_id | `str` | From ComAp customer portal<br />Or generated on API Documentation test portal using Create application registration API
| secret | `str` | From ComAp customer portal<br />Or generated on API Documentation test portal using Create application secret API

**Returns**

The bearer access token `dict` or `None` if failed.

```
{
    'token_type': `str`,
    'expires_in': `number`,
    'ext_expires_in': `number`,
    'access_token': `str` # this is the Bearer access token
}
```

---

## Class: WSV(login_id: str, key: str, token: str)

ComAp Cloud WSV API wrapper.
The `login_id` is your user name (each identity can have multiple WSV user names).

The `key` is the ComAp Key from your [Profile](https://portal.websupervisor.net/developer) (the same key as for the identity).

The `token` is the bearer token obtained from the `Identity` `authenticate` method.

*Example:*

```python
from comap import api

# ...
# Obtain the Bearer token from the example above

LOGIN_ID = ... # user name

if token is not None:
    # Create WSV instance to call APIs
    wsv = api.WSV(LOGIN_ID, COMAP_KEY, token['access_token'])
    # Call API to get the list of controller units
    units = wsv.units()
    for unit in units:
        print(f'{unit["unitGuid"]} : {unit["name"]}')
```

*Returns*

```
genset55e9*********redacted*********** : unit1 name
genset84f8*********redacted*********** : unit2 name
genset38ed*********redacted*********** : unit3 name
```

### units() -> list

Get a `list` of units with their unitGuid

**Returns**

```yaml
[{
    'name': `str`,
    'unitGuid': `str`,
    'url': `str`
}]
```

### values(unit_guid: str, value_guids: str | None = None) ‑> list

Get a `list` of values. It is recommended to specify a comma-separated list of `valueGuids` to filter the result.
You can import VALUE_GUID from `comap.constants` to get GUIDs for the most common values. Or call the method without GUID to get all values available in the controller, including their GUIDs.

| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)
| value_guids | str, optional | list of the value guids separated by comma <br /> (get it by calling this function with no parameter or `get_value_guid`) |

**Returns:**

```yaml
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
```

### info(unitGuid: str) -> list

Get information about the unit

| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)

**Return**

```yaml
{
    'name': 'str',
    'unitGuid': 'str',
    'ownerLoginId': 'str',
    'applicationType': 'str',
    'timezone': 'str',
    'connection': {
        'enabled': boolean,
        'airGateId': 'str',
        'ipAddress': 'str',
        'port': number,
        'controllerAddress': number
    },
    'position': {
        'positionType': 'str',
        'latitude': number,
        'longitude': number
    }
}
```

### comments(unitGuid: str) -> list

Get comments entered in the WebSupervisor (these can be used for maintenance tasks)
| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)

**Returns**

```yaml
[{
    "id": `number`,
    "auhtor": `str`,
    "date": `datetime`,
    "text": `str`,
    "active": `Boolean`
}]
```

### history(unit_guid: str, value_guids: str | None = None) ‑> list

Get the history of a value.

| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)
| _from | `str`, optional | history start date in format `MM/DD/YYYY`
| _to: | `str` , optional | history end date in format `MM/DD/YYYY`
| value_guids | `list`, optional | list of the value guids separated by comma <br />(get it by calling `values` or `get_value_guid`)

**Returns**

```yaml
[{
    'value': `str`,
    'validFrom': `datetime`,
    'validTo': `datetime`
}]
```

### files(unitGuid: str) -> list

Get the `list` of files stored on the controller

| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)

**Returns:**

```yaml
[{
    'fileName': `str`,
    'fileType': `str`,
    'generated': `datetime`
}]
```

### download(unit_guid: str, file_name: str, path: str = '') ‑> bool

Download a file from the controller to the current directory (or the directory specified in `path`). You can list the files using the `files` method.

| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)
| file_name | str | List names by calling `files`
| path | str, optional | Local directory to save the file (current directory if not specified)

**Returns:**

`bool`: Was the download succesful?

### command(unit_guid: str, command: str, mode: str | None = None) ‑> dict | None

This allows controlling the genset. The available commands are `start`,`stop`,`faultReset`,`changeMcb` (toggle mains circuit breaker), `changeGcb` (toggle genset circuit breaker) and `changeMode`.
For `changeMode` enter the `mode` parameter e.g. to `man` or `auto`

| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)
| command | str | see the API documentation for all possible values
|mode | str, optional | see the API documentation for all possible values

**Returns**
API response in the `JSON` format

### get_unit_guid(name: str) ‑> str | None`

Find a genset by name. Return is unitGuid

| Parameter | Type | Value |
| --- | --- | --- |
| name | str | genset name

### get_value_guid(unit_guid: str, name: str) ‑> str | None

Find a value by name. Return valueGuid

| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)
| name | str | value name

---

# comap.api_async

Same as `comap.api`, but uses a HTTPS pool session handler (for example `units(session)`, or `values(session,unitGuid,valueGuids=None)`
Check the example of use in [async example](https://github.com/bruxy70/ComAp-API/tree/development/simple-examples-async)

This module contains two classes:

- [Identity](#class-identitysession-aiohttpclientsession-key-str) - serves to authenticate to ComAp Cloud and obtain the token
             used in the individual APIs.
- [WSV](#class-wsvsession-aiohttpclientsession-login_id-str-key-str-token-str) - set of APIs to communicate with the WebSupervisor PRO

---

## Class: Identity(session: aiohttp.ClientSession, key: str)

Use `ComAp-Key`, `client_id` and `secret` to obtain the ``Bearer Token``, that is needed to authenticate to the WSV API. It uses an HTTPS pool session handler `session`.

*Example:*

```python
from comap import api_async
import aiohttp

CLIENT_ID = ... # get the id from the a repository
SECRET = ...    # get the secret from a key repository
COMAP_KEY = ... # get the key from a key repository

async def authenticate() -> str:
    async with aiohttp.ClientSession() as session:
        identity = api_async.Identity(session, COMAP_KEY)
        token = await identity.authenticate(CLIENT_ID, SECRET)
    return token

asyncio.run(authenticate())
```

*Returns*

```yaml
{
    'token_type': 'Bearer',
    'expires_in': 3599,
    'ext_expires_in': 3599,
    'access_token': 'eyJ0e***redacted***1Z_roeA'
}
```

Get the `ComAp-Key` in your [Profile](https://portal.websupervisor.net/developer), the other two values will be available on the Customer portal.

Until then, you can generate them from the API documentation using the "Try it" feature:

1. [Create Application Registration](https://portal.websupervisor.net/docs/services/comap-cloud-identity/operations/application-create?) - this will return the `client_id`.
2. [Create Application Secret](https://portal.websupervisor.net/docs/services/comap-cloud-identity/operations/application-secret-create?) - this will return the secret

These values are valid for 2 years. If you need new values, [Delete Application Registration](https://portal.websupervisor.net/docs/services/comap-cloud-identity/operations/application-delete?) and create new ones.

### authenticate(self, client_id: str, secret: str) ‑> dict | None

Authenticate and return bearer token dictionary.

| Parameter | Type | Value |
| --- | --- | --- |
| client_id | `str` | From ComAp customer portal<br />Or generated on API Documentation test portal using Create application registration API
| secret | `str` | From ComAp customer portal<br />Or generated on API Documentation test portal using Create application secret API

**Returns**

The bearer access token `dict` or `None` if failed.

```
{
    'token_type': `str`,
    'expires_in': `number`,
    'ext_expires_in': `number`,
    'access_token': `str` # this is the Bearer access token
}
```

---

## Class: WSV(session: aiohttp.ClientSession, login_id: str, key: str, token: str)

ComAp Cloud WSV API wrapper.
`session` is the HTTPS pool handler.

`login_id` is your user name (each identity can have multiple WSV user names).

`key` is the ComAp Key from your [Profile](https://portal.websupervisor.net/developer) (the same key as for the identity).

`token` is the bearer token obtained from the `Identity` `authenticate` method.

*Example:*

```python
from comap import api_async
import aiohttp

CLIENT_ID = ... # get the id from the a repository
SECRET = ...    # get the secret from a key repository
COMAP_KEY = ... # get the key from a key repository
LOGIN_ID = ...  # user name

async def main() -> None:
    async with aiohttp.ClientSession() as session:
        # Use the ComAp Cloud Identity API to get the Bearer token
        identity = api_async.Identity(session, COMAP_KEY)
        token = await identity.authenticate(CLIENT_ID, SECRET)

        if token is not None:
            # Create WSV instance to call APIs
            wsv = api_async.WSV(
                    session, 
                    LOGIN_ID, 
                    COMAP_KEY, 
                    token['access_token']
            )
            # Call API to get the list of controller units
            units = await wsv.units()
            for unit in units:
                print(f'{unit["unitGuid"]} : {unit["name"]}')

asyncio.run(main())
```

*Returns*

```
genset55e9*********redacted*********** : unit1 name
genset84f8*********redacted*********** : unit2 name
genset38ed*********redacted*********** : unit3 name
```

### units() -> list

Get a `list` of units with their unitGuid

**Returns**

```yaml
[{
    'name': `str`,
    'unitGuid': `str`,
    'url': `str`
}]
```

### values(unit_guid: str, value_guids: str | None = None) ‑> list

Get a `list` of values. It is recommended to specify a comma-separated list of `valueGuids` to filter the result.
You can import VALUE_GUID from `comap.constants` to get GUIDs for the most common values. Or call the method without GUID to get all values available in the controller, including their GUIDs.

| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)
| value_guids | str, optional | list of the value guids separated by comma <br /> (get it by calling this function with no parameter or `get_value_guid`) |

**Returns:**

```yaml
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
```

### info(unitGuid: str) -> list

Get information about the unit

| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)

**Return**

```yaml
{
    'name': 'str',
    'unitGuid': 'str',
    'ownerLoginId': 'str',
    'applicationType': 'str',
    'timezone': 'str',
    'connection': {
        'enabled': boolean,
        'airGateId': 'str',
        'ipAddress': 'str',
        'port': number,
        'controllerAddress': number
    },
    'position': {
        'positionType': 'str',
        'latitude': number,
        'longitude': number
    }
}
```

### comments(unitGuid: str) -> list

Get comments entered in the WebSupervisor (these can be used for maintenance tasks)
| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)

**Returns**

```yaml
[{
    "id": `number`,
    "auhtor": `str`,
    "date": `datetime`,
    "text": `str`,
    "active": `Boolean`
}]
```

### history(unit_guid: str, value_guids: str | None = None) ‑> list

Get the history of a value.

| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)
| _from | `str`, optional | history start date in format `MM/DD/YYYY`
| _to: | `str` , optional | history end date in format `MM/DD/YYYY`
| value_guids | `list`, optional | list of the value guids separated by comma <br />(get it by calling `values` or `get_value_guid`)

**Returns**

```yaml
[{
    'value': `str`,
    'validFrom': `datetime`,
    'validTo': `datetime`
}]
```

### files(unitGuid: str) -> list

Get the `list` of files stored on the controller

| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)

**Returns:**

```yaml
[{
    'fileName': `str`,
    'fileType': `str`,
    'generated': `datetime`
}]
```

### download(unit_guid: str, file_name: str, path: str = '') ‑> bool

Download a file from the controller to the current directory (or the directory specified in `path`). You can list the files using the `files` method.

| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)
| file_name | str | List names by calling `files`
| path | str, optional | Local directory to save the file (current directory if not specified)

**Returns:**

`bool`: Was the download succesful?

### command(unit_guid: str, command: str, mode: str | None = None) ‑> dict | None

This allows controlling the genset. The available commands are `start`,`stop`,`faultReset`,`changeMcb` (toggle mains circuit breaker), `changeGcb` (toggle genset circuit breaker) and `changeMode`.
For `changeMode` enter the `mode` parameter e.g. to `man` or `auto`

| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)
| command | str | see the API documentation for all possible values
|mode | str, optional | see the API documentation for all possible values

**Returns**
API response in the `JSON` format

### get_unit_guid(name: str) ‑> str | None`

Find a genset by name. Return is unitGuid

| Parameter | Type | Value |
| --- | --- | --- |
| name | str | genset name

### get_value_guid(unit_guid: str, name: str) ‑> str | None

Find a value by name. Return valueGuid

| Parameter | Type | Value |
| --- | --- | --- |
| unit_guid | str | the genset ID (from the `units` API, or in WSV application |front-end)
| name | str | value name
