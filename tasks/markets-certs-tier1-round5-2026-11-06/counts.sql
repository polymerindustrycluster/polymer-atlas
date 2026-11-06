-- Organization grain; generated merged exports explicitly excluded.
WITH org AS (
 SELECT * EXCLUDE(filename) FROM read_csv('data/organizations_*.csv',header=true,all_varchar=true,union_by_name=true,filename=true)
 WHERE NOT ends_with(filename,'organizations_all.csv')
)
SELECT 'active canonical organizations' AS unit_filter,count(*) AS organizations,
 count(*) FILTER (WHERE coalesce(markets_served,'')<>'') AS markets_populated,
 count(*) FILTER (WHERE coalesce(certifications,'')<>'') AS certifications_populated
FROM org WHERE status='active'
UNION ALL
SELECT 'active canonical organizations with stored Tier1 qualifier',count(*),
 count(*) FILTER (WHERE coalesce(markets_served,'')<>''),count(*) FILTER (WHERE coalesce(certifications,'')<>'')
FROM org WHERE status='active' AND coalesce(tier1_qualifier,'')<>'';
SELECT count(*) AS frame_organizations,count(DISTINCT org_id) AS unique_organizations,
 count(*) FILTER (WHERE coalesce(website,'')='') AS without_website,
 count(*) FILTER (WHERE coalesce(website,'')<>'') AS with_website,
 count(DISTINCT website) FILTER (WHERE coalesce(website,'')<>'') AS distinct_urls
FROM read_csv('tasks/markets-certs-tier1-round5-2026-11-06/frame.csv',all_varchar=true);
SELECT verdict,count(*) AS organization_enrichment_verdicts
FROM read_csv('tasks/markets-certs-tier1-round5-2026-11-06/verdicts.csv',all_varchar=true) GROUP BY verdict;
SELECT verdict,field,count(*) AS candidate_value_rows
FROM read_csv('tasks/markets-certs-tier1-round5-2026-11-06/inputs.csv',all_varchar=true) GROUP BY verdict,field;
