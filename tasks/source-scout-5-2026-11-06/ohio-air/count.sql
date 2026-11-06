SELECT
 count(*) whole_workbook_unit_rows,
 count(distinct facility_id) whole_workbook_facility_ids,
 count(*) FILTER(WHERE state='OH') state_oh_unit_rows,
 count(distinct facility_id) FILTER(WHERE state='OH') state_oh_facility_ids,
 count(*) FILTER(WHERE county IN ('Ashland','Ashtabula','Columbiana','Cuyahoga','Erie','Geauga','Huron','Lake','Lorain','Mahoning','Medina','Portage','Richland','Stark','Summit','Trumbull','Tuscarawas','Wayne')) pic18_county_only_unit_rows,
 count(distinct facility_id) FILTER(WHERE county IN ('Ashland','Ashtabula','Columbiana','Cuyahoga','Erie','Geauga','Huron','Lake','Lorain','Mahoning','Medina','Portage','Richland','Stark','Summit','Trumbull','Tuscarawas','Wayne')) pic18_county_only_facility_ids,
 count(*) FILTER(WHERE county IN ('Ashland','Ashtabula','Columbiana','Cuyahoga','Erie','Geauga','Huron','Lake','Lorain','Mahoning','Medina','Portage','Richland','Stark','Summit','Trumbull','Tuscarawas','Wayne') AND state='OH') pic18_county_and_state_oh_unit_rows,
 count(distinct facility_id) FILTER(WHERE county IN ('Ashland','Ashtabula','Columbiana','Cuyahoga','Erie','Geauga','Huron','Lake','Lorain','Mahoning','Medina','Portage','Richland','Stark','Summit','Trumbull','Tuscarawas','Wayne') AND state='OH') pic18_county_and_state_oh_facility_ids,
 count(*) FILTER(WHERE state IS DISTINCT FROM 'OH') non_oh_coded_unit_rows,
 count(distinct facility_id) FILTER(WHERE state IS DISTINCT FROM 'OH') non_oh_coded_facility_ids
FROM read_csv('/tmp/l5c-pbr.csv',all_varchar=true);
