SET memory_limit='2GB';
SET threads=4;
CREATE OR REPLACE TABLE patents AS SELECT patent_id,patent_date FROM read_csv('/tmp/l5-patents/g_patent.tsv', delim='\t',all_varchar=true) WHERE patent_date>='2020-01-01' AND withdrawn<>'1';
CREATE OR REPLACE TABLE cpc AS SELECT DISTINCT c.patent_id,cpc_subclass FROM read_csv('/tmp/l5-patents/g_cpc_current.tsv',delim='\t',all_varchar=true) c JOIN patents p USING(patent_id) WHERE starts_with(cpc_subclass,'C08') OR starts_with(cpc_subclass,'B29') OR cpc_subclass IN ('C09J','B60C');
CREATE OR REPLACE TABLE orgs AS SELECT DISTINCT a.patent_id,a.assignee_id,a.disambig_assignee_organization AS name,a.location_id FROM read_csv('/tmp/l5-patents/g_assignee_disambiguated.tsv',delim='\t',all_varchar=true) a WHERE disambig_assignee_organization<>'' AND patent_id IN (SELECT patent_id FROM cpc);
CREATE OR REPLACE TABLE locations AS SELECT * FROM read_csv('/tmp/l5-patents/g_location_disambiguated.tsv',delim='\t',all_varchar=true);
COPY (SELECT a.*,l.disambig_city AS city,l.disambig_state AS state,l.disambig_country AS country,l.county_fips,p.patent_date,string_agg(DISTINCT c.cpc_subclass,';' ORDER BY c.cpc_subclass) AS cpc FROM orgs a LEFT JOIN locations l USING(location_id) JOIN patents p USING(patent_id) JOIN cpc c USING(patent_id) GROUP BY ALL) TO '/tmp/l5-pairs.csv' (HEADER, DELIMITER ',');
SELECT 'qualifying patents' AS unit,count(DISTINCT patent_id) AS n FROM cpc;
SELECT 'qualifying organization assignees' AS unit,count(DISTINCT assignee_id) AS n FROM orgs;
