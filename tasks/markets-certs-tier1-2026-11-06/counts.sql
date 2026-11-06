-- Independent SQL recount; organization grain, active status; stored qualifier used as-is.
WITH org AS (
  SELECT * FROM read_csv('data/organizations_*.csv', header=true, all_varchar=true, union_by_name=true)
)
SELECT 'all active organizations' AS unit_filter, count(*) AS organizations,
 count(*) FILTER (WHERE coalesce(markets_served,'') <> '') AS markets_populated,
 count(*) FILTER (WHERE coalesce(certifications,'') <> '') AS certifications_populated
FROM org WHERE status='active'
UNION ALL
SELECT 'active organizations with nonempty stored tier1_qualifier', count(*),
 count(*) FILTER (WHERE coalesce(markets_served,'') <> ''),
 count(*) FILTER (WHERE coalesce(certifications,'') <> '')
FROM org WHERE status='active' AND coalesce(tier1_qualifier,'') <> '';
