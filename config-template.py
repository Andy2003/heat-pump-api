MQTT = {
    'enabled': True,
    'host': 'mosquitto',
}

INFLUXDB = {
    'enabled': False,
    'base_url': 'http://influxdb:8086',
    # Time when data should be written, even if value has not changed
    'write_through_time': 60 * 60,
    'database': 'heatpump',
    'measurement': 'heatpump',
}

BINDING = {
    'update_interval': 15,
    'heat_pump_id': 'wpl_10_ac',
    # If true, also messages not requested by us get handled
    'handle_all_messages': True,
}
