# edxapp

SELECT
  o.short_name,
  o.name,
  CONCAT('https://edxuploads.s3.amazonaws.com/', o.logo)
FROM
  organizations_organization AS o


# discovery
SELECT
  o.`key`,
  o.name,
  o.logo_image_url
FROM
  course_metadata_program_authoring_organizations ao
  JOIN course_metadata_organization o ON ao.organization_id = o.id
GROUP BY
  o.id
ORDER BY
  o.`key`;
