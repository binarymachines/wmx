# Makefile for Walmart test data pipeline


init:
	cat required_dirs.txt | xargs mkdir -p


clean: 
	rm -f temp_scripts/*
	rm -f tempdata/*
	rm -f data/*

# +open-targetblock
#
gen-params: init
	# +open-varblock(init-var)
	
	$(eval NUM_DAYS=3)

	# +close-varblock

	# +open-cmdblock(init-cmd-1)
	#
	countup --from 1 --to $(NUM_DAYS) > tempdata/daysahead.txt
	loopr -t --listfile tempdata/daysahead.txt --vartoken % --cmd-string 'datetimecalc --days % --from today' | grep "\S" > tempdata/dates.txt
	#
	# +close-cmdblock

	xcombine --listfiles=tempdata/dates.txt,static_data/zipcodes.txt --delimiter '|' \
	> tempdata/date_zip_combinations.csv
	
	cat tempdata/date_zip_combinations.csv | tuple2json --delimiter '|' --keys=date,zipcode > tempdata/input_params.json

# +close-targetblock


# +open-targetblock
#
pull-data: gen-params

	# +open-cmdblock(gen-params-1)
	#
	# use the structured input data to generate warp commands which will populate our beekeeper config templates
	#
	loopr -p -j --listfile tempdata/input_params.json --cmd-string \
	'warp --py --template-file=templates/bkpr_weatherapi.yaml.tpl --params=zipcode:{zipcode},date:{date} > tempdata/bkpr_wapi_{zipcode}_{date}.yaml' \
	> tempdata/warp_commands.txt

	# +close-cmdblock

	# +open-cmdblock(gen-params-2)
	#
	# run our generated warp commands; this will give us beekeeper config files for our date-zipcode combinations
	#  
	cat templates/shell_script_core.sh.tpl tempdata/warp_commands.txt > temp_scripts/warp_commands.sh
	chmod u+x temp_scripts/warp_commands.sh
	temp_scripts/warp_commands.sh

	# +close-cmdblock

	#
	# generate a list of beekeeper commands to call the weather API (one command per zipcode-date combination)
	#
	loopr -p -j --listfile tempdata/input_params.json --cmd-string \
	'beekeeper --config tempdata/bkpr_wapi_{zipcode}_{date}.yaml --target forecast | jq -r .data > tempdata/forecast_{zipcode}_{date}.json' \
	> tempdata/beekeeper_commands.txt

	#
	# run the beekeeper commands
	#
	cat templates/shell_script_core.sh.tpl tempdata/beekeeper_commands.txt > temp_scripts/beekeeper_commands.sh
	chmod u+x temp_scripts/beekeeper_commands.sh
	temp_scripts/beekeeper_commands.sh

# +close-targetblock


# +open-targetblock
#
manifest: pull-data
	#
	# generate a manifest
	#
	loopr -p -j --listfile tempdata/input_params.json --cmd-string 'tempdata/forecast_{zipcode}_{date}.json' \
	> tempdata/output_files.txt

	loopr -p -j --listfile tempdata/input_params.json --cmd-string '{zipcode}' > tempdata/input_zips.txt
	loopr -p -j --listfile tempdata/input_params.json --cmd-string '{date}' > tempdata/input_dates.txt

	tuplegen --delimiter '%' \
	--listfiles=tempdata/input_params.json,tempdata/input_zips.txt,tempdata/input_dates.txt,tempdata/warp_commands.txt,tempdata/beekeeper_commands.txt,tempdata/output_files.txt \
	| tuple2json --delimiter '%' --keys=params,zipcode,date,warp_cmd,beekeeper_cmd,output_file > tempdata/manifest.json

	#
	# show contents, for convenience
	#
	#cat tempdata/manifest.json | jq

# +close-targetblock

# +open-targetblock
#
process-data: manifest

	cp templates/shell_script_core.sh.tpl temp_scripts/process_forecast_data.sh

	loopr -p -j --listfile tempdata/manifest.json --cmd-string \
	'jsonfile2csv {output_file} --generator wmx_converters.ForecastConverter --delimiter "|" --params=zipcode:{zipcode} > data/forecast_data_{zipcode}_{date}.csv' \
	>> temp_scripts/process_forecast_data.sh

	chmod u+x temp_scripts/process_forecast_data.sh
	temp_scripts/process_forecast_data.sh

# +close-targetblock

# +open-targetblock
#
process-data-hourly: manifest

	loopr -p -j --listfile tempdata/manifest.json --cmd-string \
	'jsonfile2csv {output_file} --generator wmx_converters.HourlyForecastConverter --delimiter "|" --params=zipcode:{zipcode},date:{date}' \
	> tempdata/conversion_commands.txt

	loopr -p -j --listfile tempdata/manifest.json --cmd-string \
	'data/hourly_forecast_data_{zipcode}_{date}.csv' > tempdata/conversion_outfiles.txt

	tuplegen --delimiter '%' --listfiles=tempdata/conversion_commands.txt,tempdata/conversion_outfiles.txt \
	| tuple2json --delimiter '%' --keys=command,outfile > tempdata/hourly_conversion_manifest.json

	cp templates/shell_script_core.sh.tpl temp_scripts/process_hourly_forecast_data.sh

	loopr -p -j --listfile tempdata/hourly_conversion_manifest.json --cmd-string \
	'{command} > {outfile}' >> temp_scripts/process_hourly_forecast_data.sh

	chmod u+x temp_scripts/process_hourly_forecast_data.sh
	temp_scripts/process_hourly_forecast_data.sh

# +close-targetblock 	

diagnostic:

	beekeeper --config tempdata/bkpr_wapi_07086_2022-11-30.yaml \
	--target forecast | jq -r .data | jq .forecast.forecastday | jq .[0].date


requirements:
	pipenv lock -r > requirements.txt


