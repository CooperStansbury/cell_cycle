# Nextflow Working Directory

Internal directory created by Nextflow to store pipeline metadata and caching information. Files here are generated automatically and typically not edited manually. It is safe to remove when cleaning up working directories or before committing results.

If disk space becomes limited, this directory can be purged with `nextflow clean` or simply removed; it will be regenerated on the next pipeline run.

