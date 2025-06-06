-- WITH stop_words_en AS (
--     SELECT * FROM unnest(
--         ARRAY[
--             'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 
--             'any', 'are', 'aren''t', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 
--             'below', 'between', 'both', 'but', 'by', 'can''t', 'cannot', 'could', 'couldn''t', 
--             'did', 'didn''t', 'do', 'does', 'doesn''t', 'doing', 'don''t', 'down', 'during', 
--             'each', 'few', 'for', 'from', 'further', 'had', 'hadn''t', 'has', 'hasn''t', 'have', 
--             'haven''t', 'having', 'he', 'he''d', 'he''ll', 'he''s', 'her', 'here', 'here''s', 'hers', 
--             'herself', 'him', 'himself', 'his', 'how', 'how''s', 'i', 'i''d', 'i''ll', 'i''m', 'i''ve', 
--             'if', 'in', 'into', 'is', 'isn''t', 'it', 'it''s', 'its', 'itself', 'let''s', 'me', 'more', 
--             'most', 'mustn''t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 
--             'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan''t', 'she', 
--             'she''d', 'she''ll', 'she''s', 'should', 'shouldn''t', 'so', 'some', 'such', 't', 'than', 
--             'that', 'that''s', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'there''s', 
--             'these', 'they', 'they''d', 'they''ll', 'they''re', 'they''ve', 'this', 'those', 'through', 'to', 
--             'too', 'under', 'until', 'up', 'very', 'was', 'wasn''t', 'we', 'we''d', 'we''ll', 'we''re', 'we''ve', 
--             'were', 'weren''t', 'what', 'what''s', 'when', 'when''s', 'where', 'where''s', 'which', 'while', 
--             'who', 'whom', 'why', 'why''s', 'will', 'with', 'won''t', 'would', 'wouldn''t', 'you', 'you''d', 
--             'you''ll', 'you''re', 'you''ve', 'your', 'yours', 'yourself', 'yourselves'
--         ]
--     ) AS word
-- )

-- , stop_words_fr AS (
--     SELECT * FROM unnest(
--         ARRAY[
--             'le', 'la', 'les', 'l''', 'un', 'une', 'des', 'du', 'au', 'aux', 'ce', 'cet', 'cette', 'ces',
--             'à', 'de', 'en', 'sur', 'sous', 'dans', 'par', 'pour', 'avec', 'contre', 'entre', 'vers', 'chez', 
--             'hors', 'jusque', 'malgré', 'parmi', 'sauf', 'selon', 'suivant', 'via',
--             'je', 'tu', 'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles', 'moi', 'toi', 'lui', 'leur', 
--             'ceci', 'cela', 'celui', 'celle', 'ceux', 'celles',
--             'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'son', 'sa', 'ses', 'notre', 'nos', 'votre', 'vos', 'leur', 'leurs',
--             'et', 'ou', 'mais', 'donc', 'or', 'ni', 'car', 'si', 'que', 'quand', 'lorsque', 'dès', 'puis', 
--             'ainsi', 'aussi', 'alors', 'encore', 'bien', 'déjà', 'tout', 'très', 'trop', 'peu', 'même', 'toutefois', 
--             'cependant', 'pourtant', 'néanmoins', 'd’ailleurs', 'en effet', 'enfin', 'ensuite',
--             'ne', 'pas', 'plus', 'ni', 'aucun', 'rien', 'jamais', 'sans', 'non', 'oui', 'peut-être', 'sauf', 'moins',
--             'chaque', 'plusieurs', 'quelque', 'quelqu’un', 'quelque chose', 'tout', 'tous', 'toutes', 'toute', 
--             'certains', 'certaines','est','qui'
--         ]
--     ) AS word
-- )

-- , cleaned_data AS (
--     SELECT DISTINCT
--         rating,
--         CASE 
--             WHEN bank_name = 'Ait lamine Shopping' THEN 'Umnia Bank' 
--             ELSE LOWER(REGEXP_REPLACE(bank_name, '[^\w\s]', '', 'g'))
--         END AS bank_name,
--         LOWER(REGEXP_REPLACE(branche_name, '[^\w\s]', '', 'g')) AS branche_name,
--         LOWER(REGEXP_REPLACE(address, '[^\w\s]', '', 'g')) AS address,
--         LOWER(REGEXP_REPLACE(review, '[^\w\s]', '', 'g')) AS review_cleaned,
--         MD5(LOWER(REGEXP_REPLACE(review, '[^\w\s]', '', 'g'))) AS review_hash,
--         review_date
--     FROM public.bank_agency_reviews
--     WHERE review IS NOT NULL AND LENGTH(review) > 5
-- )

-- , cleaned_reviews AS (
--     SELECT DISTINCT ON (review_hash)
--         rating,
--         bank_name,
--         branche_name,
--         address,
--         ARRAY_TO_STRING(
--             ARRAY(
--                 SELECT word FROM unnest(string_to_array(review_cleaned, ' ')) AS word
--                 WHERE LOWER(word) NOT IN (SELECT word FROM stop_words_en)
--                   AND LOWER(word) NOT IN (SELECT word FROM stop_words_fr)
--             ),
--             ' '
--         ) AS review,
--         review_date
--     FROM cleaned_data
-- )

-- SELECT
--     rating,
--     bank_name,
--     branche_name,
--     address,
--     review,
--     review_date
-- FROM cleaned_reviews

WITH stop_words_en AS (
    SELECT * FROM unnest(
        ARRAY[
            'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 
            'any', 'are', 'aren''t', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 
            'below', 'between', 'both', 'but', 'by', 'can''t', 'cannot', 'could', 'couldn''t', 
            'did', 'didn''t', 'do', 'does', 'doesn''t', 'doing', 'don''t', 'down', 'during', 
            'each', 'few', 'for', 'from', 'further', 'had', 'hadn''t', 'has', 'hasn''t', 'have', 
            'haven''t', 'having', 'he', 'he''d', 'he''ll', 'he''s', 'her', 'here', 'here''s', 'hers', 
            'herself', 'him', 'himself', 'his', 'how', 'how''s', 'i', 'i''d', 'i''ll', 'i''m', 'i''ve', 
            'if', 'in', 'into', 'is', 'isn''t', 'it', 'it''s', 'its', 'itself', 'let''s', 'me', 'more', 
            'most', 'mustn''t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 
            'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan''t', 'she', 
            'she''d', 'she''ll', 'she''s', 'should', 'shouldn''t', 'so', 'some', 'such', 't', 'than', 
            'that', 'that''s', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'there''s', 
            'these', 'they', 'they''d', 'they''ll', 'they''re', 'they''ve', 'this', 'those', 'through', 'to', 
            'too', 'under', 'until', 'up', 'very', 'was', 'wasn''t', 'we', 'we''d', 'we''ll', 'we''re', 'we''ve', 
            'were', 'weren''t', 'what', 'what''s', 'when', 'when''s', 'where', 'where''s', 'which', 'while', 
            'who', 'whom', 'why', 'why''s', 'will', 'with', 'won''t', 'would', 'wouldn''t', 'you', 'you''d', 
            'you''ll', 'you''re', 'you''ve', 'your', 'yours', 'yourself', 'yourselves'
        ]
    ) AS word
), stop_words_fr AS (
    SELECT * FROM unnest(
        ARRAY[
            'le', 'la', 'les', 'l''', 'un', 'une', 'des', 'du', 'au', 'aux', 'ce', 'cet', 'cette', 'ces',
            'à', 'de', 'en', 'sur', 'sous', 'dans', 'par', 'pour', 'avec', 'contre', 'entre', 'vers', 'chez', 
            'hors', 'jusque', 'malgré', 'parmi', 'sauf', 'selon', 'suivant', 'via',
            'je', 'tu', 'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles', 'moi', 'toi', 'lui', 'leur', 
            'ceci', 'cela', 'celui', 'celle', 'ceux', 'celles',
            'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'son', 'sa', 'ses', 'notre', 'nos', 'votre', 'vos', 'leur', 'leurs',
            'et', 'ou', 'mais', 'donc', 'or', 'ni', 'car', 'si', 'que', 'quand', 'lorsque', 'dès', 'puis', 
            'ainsi', 'aussi', 'alors', 'encore', 'bien', 'déjà', 'tout', 'très', 'trop', 'peu', 'même', 'toutefois', 
            'cependant', 'pourtant', 'néanmoins', 'd’ailleurs', 'en effet', 'enfin', 'ensuite',
            'ne', 'pas', 'plus', 'ni', 'aucun', 'rien', 'jamais', 'sans', 'non', 'oui', 'peut-être', 'sauf', 'moins',
            'chaque', 'plusieurs', 'quelque', 'quelqu’un', 'quelque chose', 'tout', 'tous', 'toutes', 'toute', 
            'certains', 'certaines','est','qui'
        ]
    ) AS word
), cleaned_data AS (
    SELECT DISTINCT
        rating,
        CASE 
            WHEN bank_name = 'Ait lamine Shopping' THEN 'Umnia Bank' 
            ELSE LOWER(REGEXP_REPLACE(bank_name, '[^\w\s]', '', 'g'))
        END AS bank_name,
        LOWER(REGEXP_REPLACE(branche_name, '[^\w\s]', '', 'g')) AS branche_name,
        LOWER(REGEXP_REPLACE(address, '[^\w\s]', '', 'g')) AS address,
        LOWER(REGEXP_REPLACE(review, '[^\w\s]', '', 'g')) AS review_cleaned,
        MD5(LOWER(REGEXP_REPLACE(review, '[^\w\s]', '', 'g'))) AS review_hash,
        review_date,
        scrapping_date
    FROM public.bank_agency_reviews
    WHERE review IS NOT NULL AND LENGTH(review) > 5
), cleaned_reviews AS (
    SELECT DISTINCT ON (review_hash)
        rating,
        bank_name,
        branche_name,
        address,
        ARRAY_TO_STRING(
            ARRAY(
                SELECT word FROM unnest(string_to_array(review_cleaned, ' ')) AS word
                WHERE LOWER(word) NOT IN (SELECT word FROM stop_words_en)
                  AND LOWER(word) NOT IN (SELECT word FROM stop_words_fr)
            ),
            ' '
        ) AS review,
        review_date,
        scrapping_date
    FROM cleaned_data
)

SELECT
    rating,
    bank_name,
    branche_name,
    address,
    review,
    review_date,
    scrapping_date
FROM cleaned_reviews
