# 
# YAML init file for beekeeper 
#
#
globals:
    project_home: $WMX_HOME
    service_module: wmx_services
    processor_module: wmx_processors
    macro_module: wmx_macros

service_objects:

macros:
  
targets:
        
    forecast:
      url: https://api.weatherapi.com/v1/forecast.json
      method: GET

      request_params:
        - name: key
          value: $WAPI_KEY          

        - name: q
          value: {zipcode}

        - name: dt
          value: {date}