def handler (params, context):
    try:
        current_temperature = float(params["current_temperature"])
        daily_rain_sum = params["daily_rain_sum"]
        daily_max_temp = params["daily_max_temp"]
        daily_min_temp = params["daily_min_temp"]
    except:
        # TODO: error
        return {}

    msg = f"""
    The current temperature is {current_temperature}.
    The minimum temperature for the next 3 days will be: {daily_min_temp}.
    The maximum temperature for the next 3 days will be: {daily_max_temp}.
    The cumulated rainfall for the next 3 days will be: {daily_rain_sum}.
    """

    response = {}
    response["response"] = msg

    return response
