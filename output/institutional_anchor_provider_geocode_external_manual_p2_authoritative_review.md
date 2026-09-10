# Institutional Anchor P2 Authoritative Review

## TLDR

- Status: `p2_authoritative_review_has_accepted_rows`.
- Production model/rank/dashboard change: `False`.
- Target rows: `8`.
- Authoritative source rows: `19`.
- NPPES rows found: `5`.
- Validator accept rows staged: `8`.
- Held rows: `0`.
- Decision: Prepared validator-ready reviewed results for the P2 external-follow-up rows using provider-site, NPPES where available, and official county-equivalent references.
- Next action: Dry-run `scripts/accept_institutional_anchor_provider_geocode_external_manual_results.py` against the P2 authoritative results file, apply only if accepted metrics and conflicts are clean, then rebuild institutional source-maturity artifacts.

## Sources

| Provider | Source | URL | Evidence |
|---|---|---|---|
| 400115 | Hospital Wilma N. Vazquez provider site | https://www.wilmamed.com/contacto | Provider contact page lists the hospital at Carr. Num. 2 Km. 39.5 in Vega Baja, PR. |
| 400115 | U.S. Census TIGERweb Puerto Rico county-equivalents | https://tigerweb.geo.census.gov/tigerwebmain/Files/acs24/tigerweb_acs24_county_2020_tab20_pr.html | Official Census TIGERweb county table maps Vega Baja Municipio to GEOID 72145. |
| 480002 | Gov. Juan F. Luis Hospital provider site | https://jflusvi.org/guest-services/ | Provider site contact block lists 4007 Estate Diamond Ruby, Christiansted, St. Croix USVI. |
| 480002 | U.S. Census TIGERweb U.S. Virgin Islands county-equivalents | https://tigerweb.geo.census.gov/tigerwebmain/TIGERweb_tabblock_census2020_vi.html | Official Census TIGERweb county-based files list St. Croix as county-equivalent GEOID 78010. |
| 224039 | Haverhill Pavilion provider site | https://www.haverhillpavilion.com/about/location/ | Provider site lists Haverhill Pavilion Behavioral Health Hospital at 76 Summer St, Haverhill, MA 01830. |
| 224039 | Massachusetts Municipal Association | https://www.mma.org/community/haverhill/ | MMA community profile identifies Haverhill's county as Essex. |
| 403027 | NPPES/NPI Registry API | https://npiregistry.cms.hhs.gov/api/?number=1891120648&version=2.1 | NPPES lists Multy Medical Facilities Corp / Multy Medical Physical Rehabilitation Hospital at 402 Munoz Rivera Ave, San Juan, PR. |
| 403027 | U.S. Census TIGERweb Puerto Rico county-equivalents | https://tigerweb.geo.census.gov/tigerwebmain/Files/acs24/tigerweb_acs24_county_2020_tab20_pr.html | Official Census TIGERweb county table maps San Juan Municipio to GEOID 72127. |
| 400122 | Professional Hospital provider site | https://professionalhospital.net/ | Provider site states Professional Hospital Guaynabo is on Avenida Las Cumbres in Guaynabo. |
| 400122 | NPPES/NPI Registry API | https://npiregistry.cms.hhs.gov/api/?number=1922254952&version=2.1 | NPPES lists Professional Hospital Guaynabo Inc at Ave Las Cumbres / Street 199 Km 1.2, Guaynabo, PR. |
| 400122 | U.S. Census TIGERweb Puerto Rico county-equivalents | https://tigerweb.geo.census.gov/tigerwebmain/Files/acs24/tigerweb_acs24_county_2020_tab20_pr.html | Official Census TIGERweb county table maps Guaynabo Municipio to GEOID 72061. |
| 400137 | Doctors' Center Hospital provider site | https://www.doctorscenterhospital.com/contact-us | Provider contact page lists Doctors' Center Hospital Dorado facility and phone. |
| 400137 | NPPES/NPI Registry API | https://npiregistry.cms.hhs.gov/api/?number=1194480806&version=2.1 | NPPES lists Doctors' Center Hospital - Orlando Health - Dorado at Road 696 / Ave Efron, Dorado, PR. |
| 400137 | U.S. Census TIGERweb Puerto Rico county-equivalents | https://tigerweb.geo.census.gov/tigerwebmain/Files/acs24/tigerweb_acs24_county_2020_tab20_pr.html | Official Census TIGERweb county table maps Dorado Municipio to GEOID 72051. |
| 400012 | UICC member profile | https://www.uicc.org/membership/liga-puertorriquena-contra-el-cancer-y-su-hospital-oncologico-dr-isaac-gonzalez-martinez | UICC profile places Hospital Oncologico Dr. Isaac Gonzalez Martinez in the Puerto Rico Medical Center in San Juan. |
| 400012 | NPPES/NPI Registry API | https://npiregistry.cms.hhs.gov/api/?number=1407852338&version=2.1 | NPPES lists Hospital Oncologico Dr. Isaac Gonzalez Martinez at Bo Monacillos / Ave Americo Miranda, San Juan, PR. |
| 400012 | U.S. Census TIGERweb Puerto Rico county-equivalents | https://tigerweb.geo.census.gov/tigerwebmain/Files/acs24/tigerweb_acs24_county_2020_tab20_pr.html | Official Census TIGERweb county table maps San Juan Municipio to GEOID 72127. |
| 400010 | Puerto Rico Department of Health HIV Services Directory | https://directoriovih.salud.pr.gov/Home/Detalles/4503221 | Puerto Rico health directory lists Hospital General Castaner at Carr. 135 Km. 4.5, Castaner Lares, PR 00631 and PO Box 1003. |
| 400010 | U.S. Census TIGERweb Puerto Rico county-equivalents | https://tigerweb.geo.census.gov/tigerwebmain/Files/acs24/tigerweb_acs24_county_2020_tab20_pr.html | Official Census TIGERweb county table maps Lares Municipio to GEOID 72081. |

## Metrics

| Metric | Value |
|---|---:|
| `target_priority` | P2 |
| `target_rows` | 8 |
| `authoritative_source_rows` | 19 |
| `nppes_configured_rows` | 5 |
| `nppes_found_rows` | 5 |
| `authority_fips_mapped_rows` | 8 |
| `reviewer_accept_rows` | 8 |
| `held_rows` | 0 |
| `accepted_candidate_counties` | 7 |
| `production_model_rank_or_dashboard_change` | False |

## Reviewed Rows

| Provider | Decision | FIPS | County | Score | Checks | Issue |
|---|---|---|---|---:|---|---|
| 400115 HOSPITAL WILMA N VAZQUEZ | accept | 72145 | Vega Baja Muno | 0.8800 | provider_or_nppes_name_support; provider_or_authority_city_support; expected_fips_state_matches_provider_state; two_or_more_authoritative_sources; prior_osm_candidate_same_fips; provider_site_county_reference_used_without_nppes | Official provider/NPPES evidence and official county-equivalent references support this county assignment. |
| 480002 GOV. JUAN F. LUIS HOSPITAL | accept | 78010 | St. Croix Island | 1.0000 | provider_or_nppes_name_support; provider_or_authority_city_support; expected_fips_state_matches_provider_state; two_or_more_authoritative_sources; nppes_npi_found; nppes_active; nppes_state_matches_provider; nppes_zip_prefix_support | Official provider/NPPES evidence and official county-equivalent references support this county assignment. |
| 224039 HAVERHILL PAVILION | accept | 25009 | Essex County, Massachusetts | 0.8000 | provider_or_nppes_name_support; provider_or_authority_city_support; expected_fips_state_matches_provider_state; two_or_more_authoritative_sources; provider_site_county_reference_used_without_nppes | Official provider/NPPES evidence and official county-equivalent references support this county assignment. |
| 403027 MULTY MEDICAL FACILITIES | accept | 72127 | San Juan Muno | 1.0000 | provider_or_nppes_name_support; provider_or_authority_city_support; expected_fips_state_matches_provider_state; two_or_more_authoritative_sources; prior_osm_candidate_same_fips; nppes_npi_found; nppes_active; nppes_state_matches_provider; nppes_zip_prefix_support | Official provider/NPPES evidence and official county-equivalent references support this county assignment. |
| 400122 PROFESSIONAL HOSPITAL | accept | 72061 | Guaynabo Muno | 1.0000 | provider_or_nppes_name_support; provider_or_authority_city_support; expected_fips_state_matches_provider_state; two_or_more_authoritative_sources; prior_osm_candidate_same_fips; nppes_npi_found; nppes_active; nppes_state_matches_provider; nppes_zip_prefix_support | Official provider/NPPES evidence and official county-equivalent references support this county assignment. |
| 400137 DOCTORS CENTER HOSPITAL OH-DORADO | accept | 72051 | Dorado Muno | 1.0000 | provider_or_nppes_name_support; provider_or_authority_city_support; expected_fips_state_matches_provider_state; two_or_more_authoritative_sources; nppes_npi_found; nppes_active; nppes_state_matches_provider; nppes_zip_prefix_support | Official provider/NPPES evidence and official county-equivalent references support this county assignment. |
| 400012 HOSPITAL I GONZALEZ MARTINEZ | accept | 72127 | San Juan Muno | 1.0000 | provider_or_nppes_name_support; provider_or_authority_city_support; expected_fips_state_matches_provider_state; two_or_more_authoritative_sources; nppes_npi_found; nppes_active; nppes_state_matches_provider; nppes_zip_prefix_support | Official provider/NPPES evidence and official county-equivalent references support this county assignment. |
| 400010 CASTANER HOSPITAL | accept | 72081 | Lares Muno | 0.8800 | provider_or_nppes_name_support; provider_or_authority_city_support; expected_fips_state_matches_provider_state; two_or_more_authoritative_sources; prior_osm_candidate_same_fips; provider_site_county_reference_used_without_nppes | Official provider/NPPES evidence and official county-equivalent references support this county assignment. |

## Boundary

- This artifact only stages reviewed rows for the external/manual acceptance validator.
- It does not append overrides by itself.
- Keep institutional anchors report-only until provider geocode, source maturity, leakage, and model-impact gates clear.
