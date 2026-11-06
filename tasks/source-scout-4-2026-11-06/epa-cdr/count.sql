WITH source AS (
 SELECT *, regexp_matches(coalesce("SITE NAICS CODE 1",''),'^(3252[0-9]{2}|326[0-9]{3})\b')
 OR regexp_matches(coalesce("SITE NAICS CODE 2",''),'^(3252[0-9]{2}|326[0-9]{3})\b')
 OR regexp_matches(coalesce("SITE NAICS CODE 3",''),'^(3252[0-9]{2}|326[0-9]{3})\b') AS in_slice
 FROM read_csv('/tmp/l5b-cdr/manufacture_utf8.csv',all_varchar=true)
)
SELECT count(*) AS input_rows,count(DISTINCT "EPA-TSCA PROGRAM ID") AS all_site_ids,
 count(*) FILTER(WHERE in_slice) AS slice_rows,
 count(DISTINCT "EPA-TSCA PROGRAM ID") FILTER(WHERE in_slice) AS slice_site_ids FROM source;
