"""
Text constants for ComAp API
"""

COMAP_KEY = "Comap-Key"
AUTHORIZATION = "Authorization"
TIMEOUT = 30

IDENTITY_URL = {
    'authenticate': 'https://api.websupervisor.net/identity/application/authenticate'    
}

WSV_URL = {
    'units':   'https://api.websupervisor.net/v1.1/{login_id}/units',
    'values':  'https://api.websupervisor.net/v1.1/{login_id}/units/{unit_guid}/values',
    'info':    'https://api.websupervisor.net/v1.1/{login_id}/units/{unit_guid}/info',
    'history': 'https://api.websupervisor.net/v1.1/{login_id}/units/{unit_guid}/history',
    'files':   'https://api.websupervisor.net/v1.1/{login_id}/units/{unit_guid}/files',
    'command': 'https://api.websupervisor.net/v1.1/{login_id}/units/{unit_guid}/command',
    'comments':'https://api.websupervisor.net/v1.1/{login_id}/units/{unit_guid}/comments',
    'download':'https://api.websupervisor.net/v1.1/{login_id}/unit/{unit_guid}/download/{file_name}'
}

VALUE_GUID = {
    "genset_name":      "7b2ae258-65a8-40dd-bb42-5455753679f9",
    "serial_number":    "6253525D-CF01-4a15-A34B-6C232496E7B4",
    "last_update":      "0C9117DA-495A-11DF-85EB-428556D89593",
    "comm_state":       "F0219C1C-1860-4b4d-8E6E-3CEC96279D6F",
    "unit_state":       "48EC10D1-7AF8-4ce9-B5B3-A5315993FEB3",
    "unit_changed":     "52C8C105-49E6-477B-B43D-33FD46F54640",
    "controller":       "B9FF3CE7-0A81-4D80-8029-99C24A0E764F",
    "alarm_list":       "7EDE9575-FEB5-4540-9153-A3B9CF60DE9F",
    "alarm_list_ext":   "5E36C1AA-A2B7-4264-96B5-BB975E48B547",
    "mode":             "6a12aed6-3be0-44c4-9110-9ea33cfe3ccc",
    "nominal_power":    "72D0295A-3E65-11DF-892C-D6A856D89593",
    "actual_power":     "EE83E7E9-7453-4e64-A5CB-C8C093FB2A2F",
    "engine_state":     "BB2D1ADE-740E-488d-853B-6BA970D52E27",
    "breaker_state":    "B7E5B9B1-9F5E-45c1-82F4-3A336F1F97FA",
    "Gcb_mode":         "b0f910f3-14e4-4bd1-8db1-739e26680b9c",
    "Mcb_mode":         "5bbc94e2-2497-4d2b-a3e6-1c798d0b6430",
    "import_kWh":       "4C214D52-3D75-11DF-8AA2-529056D89593",
    "U_L1":             "4a2a2694-3049-4a8e-ba5f-cc6feeda9d59",
    "U_L2":             "e0f2f0ff-0627-4d78-bc78-8973ae8b7cea",
    "U_L3":             "201b5a65-e4b8-49e6-8f47-9144607eaf58",
    "modes_available":  "49424e2b-1009-471c-b8e3-3e84e9c16159",
    "engine_state":     "BB2D1ADE-740E-488d-853B-6BA970D52E27",
    "U_battery":        "e707bcd1-2735-4ab7-8a8c-d75fd589052c",
    "RPM":              "6629f84f-4b79-43c2-ab33-1f27f1f8c42b",
    "nominal_RPM":      "DFBA9743-A4E9-4759-89A9-845E861AD9FF",
    "frequency_gen":    "1a3767fd-72e9-429b-a088-95318804ce8e",
    "base_load":        "D23D6768-AAD0-11DF-8C33-2A13DFD72085",
    "P_mains":          "d61be5b5-56fa-4cd8-9fb7-00d2c01627ad",
    "Q_mains":          "441ef9cc-fdec-4064-8939-825be28a97b0",
    "Object_P":         "87a22d69-b0b7-48ba-bf5f-c3979b462b50",
    "fuel_level":       "0dc2739f-0fc9-4a17-bc91-26e5dda19ed8",
    "service_time_Sd":  "4ef4bd3d-d8dd-45ff-93a0-b82320fddef2",
    "service_time_1":   "57d26063-6237-489c-9e59-091c0ed13c47",
    "service_time_3":   "b5719e22-2620-414b-b36b-54975efe3dd0",
    "run_hours":        "74200D25-93F2-4328-B1D6-1A08923AA499",
    "number_of_starts": "80042f38-a6d4-4767-a730-b573e7a0dae0",
    "service_info":     "416E416A-CA43-4064-948E-479247B12411"
}
