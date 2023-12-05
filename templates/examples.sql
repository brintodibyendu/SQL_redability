-- base 1
SELECT 
    user_id,
    total_orders,
    revenue / total_orders AS average_order_value
FROM 
    sales_data
WHERE 
    total_orders IS NOT NULL AND
    total_orders > 0;



SELECT t.name FROM Team t JOIN Team_Attributes ta ON t.id = ta.team_api_id GROUP BY t.id HAVING avg(ta.overall_rating) > 70 LIMIT 0, 1000

-- update true
INSERT INTO Player VALUES (101, "Jane Doe", 983421, 1776, 166, "left", "low", "low", 190.14, 166)


WITH TeamMatches AS ( SELECT t.team_api_id, t.team_long_name, COUNT(*) AS total_matches, SUM( CASE WHEN m.home_team_goal > m.away_team_goal THEN 1 ELSE 0 END ) AS wins FROM Team AS t JOIN Matcher AS m ON t.team_api_id = m.home_team_api_id OR t.team_api_id = m.away_team_api_id GROUP BY t.team_api_id, t.team_long_name ) SELECT tm.team_long_name FROM TeamMatches AS tm WHERE tm.wins > tm.total_matches / 2
