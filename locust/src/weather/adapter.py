def handler (params, context):
    try:
        current_temperature = float(params["current_temperature"])
        daily_rain_sum = params["daily_rain_sum"]
        daily_max_temp = params["daily_max_temp"]
        daily_min_temp = params["daily_min_temp"]
    except:
        # TODO: error
        return {}

    prompt = f"""
    Write a brief summary of the weather forecast for the next 3 days, based
    on the following data.\n
    The current temperature is {current_temperature}.
    The minimum temperature for the next 3 days will be: {daily_min_temp}.
    The maximum temperature for the next 3 days will be: {daily_max_temp}.
    The cumulated rainfall for the next 3 days will be: {daily_rain_sum}.
    """

    response = {}
    if "gemini_api_key" in params:
        response["gemini_api_key"] = params["gemini_api_key"]
    response["prompt"] = prompt

    return response
