# Zenodo/GitHub Metadata Checklist

Final metadata status after the first Zenodo release.

## Required / strongly recommended

- [ ] Final software/repository title
- [x] All authors in `CITATION.cff`
- [x] All creators in `.zenodo.json`
- [x] Institutional affiliations
- [x] ORCID IDs supplied for Zhihua Cheng and Omar K. Farha
- [x] GitHub repository URL
- [x] Final version number: v1.0.0
- [x] Release date: 2026-09-08
- [x] Associated manuscript title
- [ ] Manuscript DOI — not yet available
- [x] Funding/grant and facilities information
- [ ] Related DOI or publication identifiers in Zenodo metadata, if applicable
- [x] Copyright holder in `LICENSE`: Northwestern University
- [ ] Check that no confidential/personal files are present
- [x] Zenodo DOI: `10.5281/zenodo.22665064`

## Zenodo/GitHub release workflow

1. Create a **public** GitHub repository.
2. Upload the files in this package.
3. Commit the edited metadata files.
4. Connect the repository in Zenodo's GitHub integration.
5. Create a GitHub release, e.g. `v1.0.0`.
6. Zenodo will ingest the release and create a DOI.
7. After Zenodo creates the DOI, update `CITATION.cff` and the README if desired.
8. Do not rewrite an already-published Zenodo record; create a new version/release when making substantive changes.

## Important metadata rule

If both `.zenodo.json` and `CITATION.cff` are present, Zenodo uses `.zenodo.json`
for GitHub release archiving. Keep the two files consistent.
