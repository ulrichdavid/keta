-- get average active page dwell and aggregate impressions from top 50 publishers by traffic
SELECT AVG(m.active_page_dwell) as apd, SQ.referer_host as host, COUNT(*) as impressions FROM
arion.prod.fact_moat_viewability m
LEFT OUTER JOIN
    (SELECT uuid_str_to_bin(uuid) as bin_id, referer_host
       FROM tracker.prod.event
       WHERE time_id >= 2017050100 and time_id <= 2017060100
       AND referer_host IN
        (SELECT referer_host FROM tracker.prod.event
         WHERE time_id >= 2017050100 and time_id <= 2017060100
       AND referer_host != 'unknown'
       AND referer_host NOT LIKE '%doubleclick.net%'
       GROUP BY referer_host
       ORDER BY COUNT(*) DESC
       LIMIT 50)
     )
     AS SQ ON SQ.bin_id = uuid_str_to_bin(m.impression_id)
WHERE time_id >= 2017050100 and time_id <= 2017060100
GROUP BY SQ.referer_host
ORDER BY SQ.referer_host ASC;

-- get average apd for top 50 sites by month
SELECT AVG(m.active_page_dwell) as apd, SQ.referer_host as host, COUNT(*) as impressions FROM
arion.prod.fact_moat_viewability m
LEFT OUTER JOIN
    (SELECT uuid_str_to_bin(uuid) as bin_id, referer_host
       FROM tracker.prod.event
       WHERE time_id >= 2017050100 and time_id <= 2017050300
       AND referer_host IN
        (SELECT referer_host FROM tracker.prod.event
         WHERE time_id >= 2017050100 and time_id <= 2017050300
       AND referer_host != 'unknown'
       AND referer_host NOT LIKE '%doubleclick.net%'
       AND referer_host NOT LIKE '%ampproject.net%'
       GROUP BY referer_host
       ORDER BY COUNT(*) DESC
       LIMIT 50)
     )
     AS SQ ON SQ.bin_id = uuid_str_to_bin(m.impression_id)
WHERE time_id >= 2017050100 and time_id <= 2017060100
AND host IS NOT NULL
GROUP BY SQ.referer_host
ORDER BY SQ.referer_host ASC;

-- most relevant articles
SELECT SUM(c) as relevant, host FROM(
SELECT count(DISTINCT referer) as c, referer_host as host
FROM tracker.prod.event
WHERE referer IN
    (SELECT referer
    FROM tracker.prod.event
    WHERE time_id >= 2017050100 and time_id <= 2017050300 //window observation
    AND referer_host='time.com' //change this to IN... for list of top publishers
    GROUP BY referer
    LIMIT 10)
AND time_id > 2017041000 AND time_id < 2017050100 // how far back we want to check
GROUP BY referer, host)
GROUP BY host;

-- grab stale content count (relevancy) based on May impressions
SELECT count(*) as impressions, replace(referer_host,'www.','') as host, iab_id as iab FROM tracker.prod.event
LEFT JOIN pub_property_iab ON (replace(website_url,'www.','') = replace(referer_host,'www.',''))
WHERE referer_host IN
         (SELECT referer_host FROM tracker.prod.event
         WHERE time_id >= 2017050100 and time_id <= 2017060100
         // select by IAB category
         AND replace(referer_host,'www.','') IN
         (SELECT replace(website_url,'www.','') FROM pub_property_iab
          WHERE iab_id='IAB2'
         GROUP BY website_url)
         AND referer_host != 'unknown'
         AND referer_host NOT LIKE '%doubleclick.net%'
         AND referer_host NOT LIKE '%ampproject.net%'
         GROUP BY referer_host
         ORDER BY COUNT(*) DESC)
  AND time_id > 2017010100 and time_id < 2017050100
  AND referer_host != 'unknown'
  GROUP BY referer_host, iab_id;

  -- get average apd for iab
SELECT AVG(m.active_page_dwell) as attention, SQ.referer_host as host, COUNT(*) as impressions, IAB FROM
arion.prod.fact_moat_viewability m
LEFT OUTER JOIN
    (SELECT uuid_str_to_bin(uuid) as bin_id, referer_host, iab_id as IAB
       FROM tracker.prod.event
       LEFT JOIN pub_property_iab ON (replace(website_url,'www.','') = replace(referer_host,'www.',''))
       WHERE time_id >= 2017050100 and time_id <= 2017060100
       AND referer_host IN
        (SELECT referer_host FROM tracker.prod.event
         WHERE time_id >= 2017050100 and time_id <= 2017060100
         AND referer_host != 'unknown'
         AND referer_host NOT LIKE '%doubleclick.net%'
         GROUP BY referer_host
         ORDER BY COUNT(*) DESC)
     )
     AS SQ ON SQ.bin_id = uuid_str_to_bin(m.impression_id)
WHERE time_id >= 2017050100 and time_id <= 2017060100
AND host IS NOT NULL
GROUP BY host, IAB
ORDER BY host, IAB ASC;

-- get attention metrics by IAB category
SELECT AVG(m.active_page_dwell) as attention, SQ.referer_host as host, COUNT(*) as impressions FROM
arion.prod.fact_moat_viewability m
LEFT OUTER JOIN
    (SELECT uuid_str_to_bin(uuid) as bin_id, referer_host
       FROM tracker.prod.event
       WHERE time_id >= 2017050100 and time_id <= 2017060100
       AND referer_host IN
        (SELECT referer_host FROM tracker.prod.event
         WHERE time_id >= 2017050100 and time_id <= 2017060100
         AND
         referer_host IN (
        'www.roadandtrack.com',
        'www.dirtrider.com',
        'www.parkers.co.uk',
        'www.rides-mag.com',
        'www.classiccarsforsale.co.uk',
        'www.popularmechanics.com',
        'www.motorcyclenews.com',
        'www.carmagazine.co.uk')
       AND referer_host != 'unknown'
       AND referer_host NOT LIKE '%doubleclick.net%'
       GROUP BY referer_host
       ORDER BY COUNT(*) DESC)
     )
     AS SQ ON SQ.bin_id = uuid_str_to_bin(m.impression_id)
WHERE time_id >= 2017050100 and time_id <= 2017060100
AND host IS NOT NULL
GROUP BY host
ORDER BY host ASC;
