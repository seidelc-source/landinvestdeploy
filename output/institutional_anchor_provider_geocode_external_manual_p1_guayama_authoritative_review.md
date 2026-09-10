# Institutional Anchor P1 Guayama Authoritative Review

## TLDR

- Status: `p1_guayama_authoritative_review_has_accepted_rows`.
- Production model/rank/dashboard change: `False`.
- Target rows: `1`.
- Authoritative source rows: `4`.
- Validator accept rows staged: `1`.
- Held rows: `0`.
- Decision: Prepared validator-ready reviewed results for the Guayama row using PR Department of Health, Census TIGERweb, provider-site, prior CMS HGI conflict, and prior OSM context.
- Next action: Dry-run `scripts/accept_institutional_anchor_provider_geocode_external_manual_results.py` against the P1 Guayama authoritative results file, apply only if accepted metrics and conflicts are clean, then rebuild institutional source-maturity artifacts.

## Sources

| Source | URL | Evidence |
|---|---|---|
| Puerto Rico Department of Health | https://www.salud.pr.gov/CMS/DOWNLOAD/9591 | Official Puerto Rico Department of Health list places Hospital Menonita Guayama under Municipio Guayama with physical address 10011 Ave. Pedro Albizy U. Campos, Guayama, PR 00704 and phone (787) 864-4300. |
| U.S. Census TIGERweb | https://tigerweb.geo.census.gov/tigerwebmain/Files/bas26/tigerweb_bas26_county_2020_tab20_pr.html | Official Census county-equivalent table maps Guayama Municipio to GEOID 72057 and separately maps Guayanilla Municipio to GEOID 72059. |
| Sistema de Salud Menonita provider site | https://www.sistemamenonita.com/hospital-guayama | Provider site confirms Hospital Menonita Guayama and phone 787.864.4300; it states the system converted the acquired Guayama hospital into Hospital Menonita Guayama, Inc. |
| CMS HGI P1 territory review context | /Users/coryseidel/PersonalProjects/IdeaTests/LandInvest/output/institutional_anchor_provider_geocode_external_manual_p1_territory_cms_hgi_results.csv | Prior CMS HGI review held the row because CMS city GUAYAMA conflicted with CMS county/parish GUAYANILLA; the city supports Guayama while the CMS county/parish value is treated as conflicting. |

## Metrics

| Metric | Value |
|---|---:|
| `target_rows` | 1 |
| `authoritative_source_rows` | 4 |
| `authority_fips_mapped_rows` | 1 |
| `reviewer_accept_rows` | 1 |
| `held_rows` | 0 |
| `accepted_candidate_counties` | 1 |
| `production_model_rank_or_dashboard_change` | False |

## Reviewed Rows

| Provider | Decision | FIPS | County | Checks | Issue |
|---|---|---|---|---|---|
| 400048 HOSPITAL MENONITA GUAYAMA | accept | 72057 | Guayama Muno | provider_id_match; provider_name_supports_guayama; provider_state_pr; hcris_city_guayama; hcris_zip_puerto_rico; county_lookup_has_72057_guayama; prior_osm_candidate_guayama_held_for_precision_only; cms_hgi_prior_hold_recorded; cms_hgi_conflicting_guayanilla_value_recorded; pr_department_of_health_municipio_guayama; census_tigerweb_72057_guayama_municipio; census_tigerweb_72059_guayanilla_separate_municipio; provider_site_confirms_hospital_guayama | Official PR health, Census county-equivalent, provider-site, and local row context support Guayama Municipio. |

## Boundary

- This artifact only stages reviewed rows for the external/manual acceptance validator.
- It does not append overrides by itself.
- Keep institutional anchors report-only until provider geocode, source maturity, leakage, and model-impact gates clear.
