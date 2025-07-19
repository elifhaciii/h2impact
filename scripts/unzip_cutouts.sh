for month in {01..12}; do
  # Country code and year (update if needed)
  CODE="DE"
  YEAR="2020"

  # Make a temp dir for each month
  mkdir -p cutouts/tmp_$month

  # Unzip (assuming the NetCDF is actually a zip — correct if needed)
  unzip -o cutouts/${CODE}_${YEAR}_${month}.nc -d cutouts/tmp_$month

  # Rename the extracted files with consistent format
  mv cutouts/tmp_$month/data_stream-oper_stepType-instant.nc cutouts/${CODE}_${YEAR}_${month}_instant.nc
  mv cutouts/tmp_$month/data_stream-oper_stepType-accum.nc   cutouts/${CODE}_${YEAR}_${month}_accum.nc

  # Remove temp dir
  rm -r cutouts/tmp_$month
done

