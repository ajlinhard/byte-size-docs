# PostgreSQL Array Operations Cheat Sheet

---

## Quick Reference

| Goal | Syntax |
|---|---|
| Element access | `col[n]` |
| Slice | `col[s:e]` |
| Contains element | `val = ANY(col)` |
| Array contains array | `col @> ARRAY[...]` |
| Arrays overlap | `col && ARRAY[...]` |
| Expand to rows | `unnest(col)` |
| Expand with index | `unnest(col) WITH ORDINALITY` |
| Parallel unnest | `unnest(a, b) AS t(x, y)` |
| Aggregate to array | `array_agg(expr)` |
| Length | `array_length(col, 1)` |
| Append element | `array_append(col, val)` |
| Remove element | `array_remove(col, val)` |
| Array → string | `array_to_string(col, sep)` |
| String → array | `string_to_array(str, sep)` |

---

## 1. Creating Arrays

```sql
-- Array literal
SELECT ARRAY[1, 2, 3];

-- Array from subquery
SELECT ARRAY(SELECT id FROM users LIMIT 5);

-- Typed array
SELECT ARRAY[1, 2, 3]::int[];

-- Multi-dimensional array
SELECT ARRAY[[1, 2], [3, 4]];

-- Column definition
CREATE TABLE posts (
  id        SERIAL PRIMARY KEY,
  title     TEXT,
  tags      TEXT[],
  scores    INTEGER[]
);
```

---

## 2. Inserting Array Data

```sql
INSERT INTO posts (title, tags, scores)
VALUES
  ('Hello World',  ARRAY['postgres', 'sql', 'arrays'], ARRAY[90, 85, 92]),
  ('Deep Dives',   '{postgres,advanced}',               '{88,76,95}'),
  ('Quick Tips',   ARRAY['sql', 'tips'],                ARRAY[70, 80]);
```

---

## 3. Accessing Elements

```sql
-- 1-based indexing
SELECT tags[1]           AS first_tag  FROM posts;   -- 'postgres'
SELECT tags[2]           AS second_tag FROM posts;   -- 'sql'

-- Slicing  [start:end]
SELECT tags[1:2]         AS first_two  FROM posts;   -- {postgres,sql}

-- Last element (via array_length)
SELECT tags[array_length(tags, 1)] AS last_tag FROM posts;
```

---

## 4. Core Array Functions

```sql
-- Length of array (dimension 1)
SELECT array_length(tags, 1) FROM posts;

-- Number of elements (equivalent for 1D)
SELECT cardinality(tags) FROM posts;

-- Append / Prepend
SELECT array_append(tags, 'new')   FROM posts;
SELECT array_prepend('new', tags)  FROM posts;

-- Concatenate two arrays
SELECT array_cat(ARRAY[1,2], ARRAY[3,4]);           -- {1,2,3,4}
SELECT ARRAY[1,2] || ARRAY[3,4];                    -- {1,2,3,4}

-- Remove a value
SELECT array_remove(tags, 'sql') FROM posts;

-- Replace a value
SELECT array_replace(tags, 'sql', 'MySQL') FROM posts;

-- Reverse
SELECT array(SELECT unnest(tags) ORDER BY 1 DESC) FROM posts;

-- Positions of element (first match)
SELECT array_position(tags, 'sql') FROM posts;

-- All positions of element
SELECT array_positions(tags, 'sql') FROM posts;

-- Convert array to string
SELECT array_to_string(tags, ', ') FROM posts;      -- 'postgres, sql, arrays'

-- Convert string to array
SELECT string_to_array('a,b,c', ',');               -- {a,b,c}
```

---

## 5. Containment & Membership Operators

```sql
-- Element exists in array  (ANY)
SELECT * FROM posts WHERE 'sql' = ANY(tags);

-- Element NOT in array  (ALL)
SELECT * FROM posts WHERE 'java' <> ALL(tags);

-- Array contains another array  (@>)
SELECT * FROM posts WHERE tags @> ARRAY['sql', 'tips'];

-- Array is contained by another array  (<@)
SELECT * FROM posts WHERE tags <@ ARRAY['sql', 'tips', 'postgres'];

-- Arrays overlap (share at least one element)  (&&)
SELECT * FROM posts WHERE tags && ARRAY['sql', 'advanced'];
```

---

## 6. Unnesting Arrays

```sql
-- Expand array into rows
SELECT unnest(tags) AS tag FROM posts;

-- Unnest with ordinality (index + value)
SELECT tag, idx
FROM posts,
     unnest(tags) WITH ORDINALITY AS t(tag, idx);

-- Unnest multiple arrays in parallel (zip)
SELECT title, tag, score
FROM posts,
     unnest(tags, scores) AS t(tag, score);
```

---

## 7. Aggregating Into Arrays

```sql
-- Collect values into an array
SELECT array_agg(title) AS all_titles FROM posts;

-- With ORDER BY inside the aggregate
SELECT array_agg(title ORDER BY title) AS sorted_titles FROM posts;

-- Distinct values only
SELECT array_agg(DISTINCT tag) AS unique_tags
FROM posts, unnest(tags) AS t(tag);
```

---

## 8. Intermediate: Filtering & Transforming

```sql
-- Posts that have more than 2 tags
SELECT title, tags
FROM posts
WHERE array_length(tags, 1) > 2;

-- Unnest, filter, re-aggregate  (keep only tags starting with 'p')
SELECT title,
       array_agg(tag) AS filtered_tags
FROM posts,
     unnest(tags) AS t(tag)
WHERE tag LIKE 'p%'
GROUP BY title;

-- Compute average score per post from a scores array
SELECT title,
       (SELECT AVG(s) FROM unnest(scores) AS s) AS avg_score
FROM posts;

-- Or with a lateral join
SELECT p.title, avg_score
FROM posts p,
     LATERAL (SELECT AVG(s) AS avg_score FROM unnest(p.scores) AS s) stats;
```

---

## 9. Advanced: Joins with Array Columns

```sql
-- Setup
CREATE TABLE tags_master (
  tag_name    TEXT PRIMARY KEY,
  category    TEXT
);

INSERT INTO tags_master VALUES
  ('postgres',  'database'),
  ('sql',       'database'),
  ('advanced',  'skill'),
  ('tips',      'content'),
  ('arrays',    'feature');


-- JOIN posts to tags_master by unnesting the array
SELECT p.title, t.tag_name, tm.category
FROM posts p
JOIN LATERAL unnest(p.tags) AS t(tag_name)
          ON TRUE
JOIN tags_master tm
          ON tm.tag_name = t.tag_name;


-- LEFT JOIN to keep posts even when no tags match
SELECT p.title, t.tag_name, tm.category
FROM posts p
LEFT JOIN LATERAL unnest(p.tags) AS t(tag_name) ON TRUE
LEFT JOIN tags_master tm                          ON tm.tag_name = t.tag_name;


-- Find posts that have at least one 'database' category tag
SELECT DISTINCT p.title
FROM posts p
JOIN LATERAL unnest(p.tags) AS t(tag_name) ON TRUE
JOIN tags_master tm                         ON tm.tag_name = t.tag_name
WHERE tm.category = 'database';
```

---

## 10. Advanced: GROUP BY with Array Operations

```sql
-- Count how many posts use each tag
SELECT tag, COUNT(*) AS post_count
FROM posts,
     unnest(tags) AS t(tag)
GROUP BY tag
ORDER BY post_count DESC;


-- Category breakdown: how many distinct tags per category appear across all posts
SELECT tm.category,
       COUNT(DISTINCT t.tag_name) AS unique_tags_used,
       COUNT(*)                   AS total_usages
FROM posts p
JOIN LATERAL unnest(p.tags) AS t(tag_name) ON TRUE
JOIN tags_master tm                         ON tm.tag_name = t.tag_name
GROUP BY tm.category
ORDER BY total_usages DESC;


-- Average score per tag (unnest both arrays in parallel, then join + group)
SELECT t.tag_name,
       ROUND(AVG(s.score), 2) AS avg_score,
       COUNT(*)               AS appearances
FROM posts p
JOIN LATERAL unnest(p.tags, p.scores) AS t(tag_name, score) ON TRUE
GROUP BY t.tag_name
ORDER BY avg_score DESC;


-- Posts grouped by number of tags (histogram)
SELECT array_length(tags, 1) AS tag_count,
       COUNT(*)              AS num_posts,
       array_agg(title)      AS post_titles
FROM posts
GROUP BY array_length(tags, 1)
ORDER BY tag_count;
```

---

## 11. Advanced: Window Functions + Arrays

```sql
-- Running array of tags seen so far (by post id)
SELECT id,
       title,
       array_agg(tag) OVER (ORDER BY id) AS cumulative_tags
FROM posts,
     unnest(tags) AS t(tag);


-- Rank posts by their highest score (from scores array)
SELECT title,
       scores,
       (SELECT MAX(s) FROM unnest(scores) AS s) AS top_score,
       RANK() OVER (ORDER BY (SELECT MAX(s) FROM unnest(scores) AS s) DESC) AS rnk
FROM posts;
```

---

## 12. Advanced: Array Deduplication & Set Operations

```sql
-- Deduplicate an array (preserve order)
SELECT ARRAY(
  SELECT DISTINCT unnest(tags)
  FROM posts
  WHERE id = 1
);

-- Union of all tags across all posts (flat, distinct)
SELECT ARRAY(
  SELECT DISTINCT tag
  FROM posts, unnest(tags) AS t(tag)
  ORDER BY tag
) AS all_unique_tags;

-- Intersection of tags between two posts
SELECT ARRAY(
  SELECT unnest(p1.tags)
  INTERSECT
  SELECT unnest(p2.tags)
) AS common_tags
FROM posts p1
JOIN posts p2 ON p1.id = 1 AND p2.id = 2;

-- Difference: tags in post 1 but not post 2
SELECT ARRAY(
  SELECT unnest(p1.tags)
  EXCEPT
  SELECT unnest(p2.tags)
) AS exclusive_tags
FROM posts p1
JOIN posts p2 ON p1.id = 1 AND p2.id = 2;
```

---

## 13. Indexing Arrays for Performance

```sql
-- GIN index for containment / overlap queries  (@>, <@, &&, ANY)
CREATE INDEX idx_posts_tags_gin ON posts USING GIN (tags);

-- Now these queries can use the index:
SELECT * FROM posts WHERE tags @> ARRAY['sql'];
SELECT * FROM posts WHERE tags && ARRAY['tips', 'advanced'];
SELECT * FROM posts WHERE 'postgres' = ANY(tags);

-- For array_ops (smaller, faster when you only need equality / containment)
CREATE INDEX idx_posts_tags_gin_ops ON posts USING GIN (tags array_ops);
```

---
