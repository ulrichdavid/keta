-- select distinct uuids from the top 100 root domains in tracker
SELECT count(DISTINCT uuid) as uniques, replace(src:supply:site:domain,'"','') as domain FROM
KSSP_BID_RESPONSE_EXACT
WHERE domain IN
    (SELECT 
    CASE
        WHEN
            POSITION('.co.uk', REPLACE(referer_host,'www.','')) > 0 THEN
                REPLACE(referer_host,'www.','')
        WHEN 
            LENGTH(REPLACE(referer_host,'www.','')) - LENGTH(REPLACE(REPLACE(referer_host,'www.',''), '.', '')) > 1 THEN
                REPLACE(REPLACE(referer_host,'www.',''),LEFT(REPLACE(referer_host,'www.',''),POSITION('.',REPLACE(referer_host,'www.',''))),'')
        ELSE REPLACE(referer_host,'www.','')
    END AS referer_host
    FROM tracker.prod.event
    WHERE time_id >= 2017050100 and time_id <= 2017060100
    AND referer_host != 'unknown'
    AND referer_host NOT LIKE '%ampproject%'
    GROUP BY referer_host
    ORDER BY count(*) ASC
    LIMIT 100)
AND time_id >= 2017050100 and time_id <= 2017060100
GROUP BY domain
ORDER BY uniques DESC;


-- select top 100 domains by traffic from tracker
SELECT count(*) as Impressions,
    CASE
        WHEN
            POSITION('.co.uk', REPLACE(referer_host,'www.','')) > 0 THEN
                REPLACE(referer_host,'www.','')
        WHEN 
            LENGTH(REPLACE(referer_host,'www.','')) - LENGTH(REPLACE(REPLACE(referer_host,'www.',''), '.', '')) > 1 THEN
                REPLACE(REPLACE(referer_host,'www.',''),LEFT(REPLACE(referer_host,'www.',''),POSITION('.',REPLACE(referer_host,'www.',''))),'')
        ELSE REPLACE(referer_host,'www.','')
    END AS Domain
    FROM tracker.prod.event
    WHERE time_id >= 2017050100 and time_id <= 2017060100
    AND referer_host != 'unknown'
    AND referer_host NOT LIKE '%ampproject%'
    GROUP BY referer_host
    ORDER BY count(*) DESC
    LIMIT 100;
    
-- grab CNN daily counts for May    
SELECT
COUNT(*) as impressions,
to_date(time) as day,
CASE
    WHEN POSITION('http://',referer,10) > 1 THEN //url duplication
        LOWER(REPLACE(LEFT(referer,POSITION('http://',referer) - 1),'index.html',''))
    WHEN POSITION('https://',referer,10) > 1 THEN //url duplication
        LOWER(REPLACE(LEFT(referer,POSITION('https://',referer) - 1),'index.html',''))
    WHEN POSITION('?',referer) > 0 THEN
        LOWER(RTRIM(REPLACE(LEFT(referer,POSITION('/?',referer)),'index.html',''),'/'))
    WHEN POSITION('&',referer) > 0 THEN
        LOWER(RTRIM(REPLACE(LEFT(referer,POSITION('/&',referer)),'index.html',''),'/'))
    WHEN POSITION('@',referer) > 0 THEN
        LOWER(RTRIM(REPLACE(LEFT(referer,POSITION('/@',referer)),'index.html',''),'/'))      
    ELSE
        LOWER(RTRIM(REPLACE(referer,'/index.html',''),'/'))
END AS article
FROM tracker.prod.event
WHERE article IN
    (
      SELECT
      CASE
          WHEN POSITION('http://',referer,10) > 1 THEN //url duplication
              LOWER(REPLACE(LEFT(referer,POSITION('http://',referer) - 1),'index.html',''))
          WHEN POSITION('https://',referer,10) > 1 THEN //url duplication
              LOWER(REPLACE(LEFT(referer,POSITION('https://',referer) - 1),'index.html',''))
          WHEN POSITION('?',referer) > 0 THEN
              LOWER(RTRIM(REPLACE(LEFT(referer,POSITION('/?',referer)),'index.html',''),'/'))
          WHEN POSITION('&',referer) > 0 THEN
              LOWER(RTRIM(REPLACE(LEFT(referer,POSITION('/&',referer)),'index.html',''),'/'))
          WHEN POSITION('@',referer) > 0 THEN
              LOWER(RTRIM(REPLACE(LEFT(referer,POSITION('/@',referer)),'index.html',''),'/'))      
          ELSE
              LOWER(RTRIM(REPLACE(referer,'/index.html',''),'/'))
      END AS article  
      FROM tracker.prod.event
      WHERE time_id >= 2017050100 and time_id <= 2017060100
      AND referer_host = 'www.cnn.com'
      AND LEFT(referer,26) = 'http://www.cnn.com/2017/05'
      GROUP BY
          article
      ORDER BY
          article ASC
    )
AND time_id >= 2017050100 and time_id <= 2017061500 //trail to mid-June for 7 day buffer
AND referer_host = 'www.cnn.com'
GROUP BY
    article, day
ORDER BY
    article, day ASC;
    
-- grab top 3000 MetroLyrics daily count
SELECT
COUNT(*) as impressions,
to_date(time) as day,
CASE
    WHEN POSITION('http:/',referer,10) > 1 THEN
        LOWER(LEFT(referer,(POSITION('http:/',referer) - 1)))
    WHEN POSITION('?',referer) > 0 THEN
        LOWER(LEFT(referer,(POSITION('?',referer) - 1)))
    ELSE
        LOWER(referer)
END AS lyrics
FROM tracker.prod.event
WHERE lyrics IN
    (
      SELECT
      CASE
          WHEN POSITION('http:/',referer,10) > 1 THEN
              LOWER(LEFT(referer,(POSITION('http:/',referer) - 1)))
          WHEN POSITION('?',referer) > 0 THEN
              LOWER(LEFT(referer,(POSITION('?',referer) - 1)))
          ELSE
              LOWER(referer)
      END AS lyrics
      FROM tracker.prod.event
      WHERE time_id >= 2017050100 and time_id <= 2017060100
      AND referer_host = 'www.metrolyrics.com'
      GROUP BY
          lyrics
      ORDER BY COUNT(*) DESC
      LIMIT 3000
    )
AND time_id >= 2017050100 and time_id <= 2017061500 //trail to mid-June for 7 day buffer
AND referer_host = 'www.metrolyrics.com'
GROUP BY
    lyrics, day
ORDER BY
    lyrics, day ASC;
    
    
-- grab top 30000 littlethings daily count
SELECT
COUNT(*) as impressions,
to_date(time) as day,
CASE
    WHEN POSITION('?',referer) > 0 THEN
        LOWER(LEFT(referer,(POSITION('?',referer) - 1)))
    ELSE
        LOWER(referer)
END AS page
FROM tracker.prod.event
WHERE page IN
    (
      SELECT
      CASE
          WHEN POSITION('?',referer) > 0 THEN
              LOWER(LEFT(referer,(POSITION('?',referer) - 1)))
          ELSE
              LOWER(referer)
      END AS page
      FROM tracker.prod.event
      WHERE time_id >= 2017050100 and time_id <= 2017060100
      AND referer_host = 'www.littlethings.com'
      GROUP BY page, to_date(time)
      ORDER BY to_date(time) ASC
      LIMIT 30000
    )
AND time_id >= 2017050100 and time_id <= 2017061500 //trail to mid-June for 7 day buffer
AND referer_host = 'www.littlethings.com'
GROUP BY
    page, day
ORDER BY
    page, day ASC;
