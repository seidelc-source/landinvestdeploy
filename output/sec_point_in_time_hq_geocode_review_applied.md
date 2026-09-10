# SEC Point-In-Time HQ Geocode Review Applied

## TLDR

- Status: `report_only_geocode_review_applied`.
- Production model/rank/dashboard change: `False`.
- Manual override rows: `83`.
- Applied review rows: `367`.
- Manual applied review rows: `85`.
- Auto same-city/state/ZIP snapshot reuse rows: `282`.
- Pending geocode rows: `154`.
- Pending point-in-time geocode rows: `0`.
- County-year candidate rows: `216`.

## Applied Reviews

| queue row | company | filing date | FIPS | county | note |
| --- | --- | --- | --- | --- | --- |
| sec_pit_0227 | Air Products & Chemicals, Inc. | 2016-01-29 | 42077 | Lehigh County, Pennsylvania | Accepted report-only SEC point-in-time HQ geocode review: residual_same_city_snapshot_county_review assigned Lehigh County, Pennsylvania (42077) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0262 | CAL-MAINE FOODS INC | 2003-04-10 | 28049 | Hinds County, Mississippi | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Hinds County, Mississippi (28049) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0065 | CAL-MAINE FOODS INC | 2003-08-12 | 28049 | Hinds County, Mississippi | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Hinds County, Mississippi (28049) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0407 | TYSON FOODS, INC. | 2014-05-05 | 05143 | Washington County, Arkansas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Washington County, Arkansas (05143) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0198 | TYSON FOODS, INC. | 2014-11-17 | 05143 | Washington County, Arkansas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Washington County, Arkansas (05143) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0199 | TYSON FOODS, INC. | 2025-11-10 | 05143 | Washington County, Arkansas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Washington County, Arkansas (05143) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0408 | TYSON FOODS, INC. | 2026-05-04 | 05143 | Washington County, Arkansas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Washington County, Arkansas (05143) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0009 | AIR T INC | 2004-11-10 | 37035 | Catawba County, North Carolina | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Catawba County, North Carolina (37035) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0003 | ACORN ENERGY, INC. | 2026-03-05 | 10003 | New Castle County, Delaware | Manual point-in-time HQ review: Wilmington DE 19801 business address assigned to New Castle County for report-only SEC filing-observed address staging. |
| sec_pit_0206 | ACORN ENERGY, INC. | 2026-05-07 | 10003 | New Castle County, Delaware | Manual point-in-time HQ review: Wilmington DE 19801 business address assigned to New Castle County for report-only SEC filing-observed address staging. |
| sec_pit_0019 | ASURE SOFTWARE INC | 2004-11-29 | 48453 | Travis County, Texas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned Travis County, Texas (48453) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0178 | FUELCELL ENERGY INC | 2012-01-17 | 09001 | Fairfield County, Connecticut | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned Fairfield County, Connecticut (09001) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0148 | EXPAND ENERGY Corp | 2016-02-25 | 40109 | Oklahoma County, Oklahoma | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned Oklahoma County, Oklahoma (40109) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0149 | EXPAND ENERGY Corp | 2026-02-18 | 40109 | Oklahoma County, Oklahoma | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Oklahoma County, Oklahoma (40109) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0175 | FORWARD AIR CORP | 2015-02-20 | 47059 | Greene County, Tennessee | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned Greene County, Tennessee (47059) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0176 | FORWARD AIR CORP | 2016-02-19 | 47059 | Greene County, Tennessee | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned Greene County, Tennessee (47059) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0338 | ENERGY FOCUS, INC/DE | 2026-05-12 | 39035 | Cuyahoga County, Ohio | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned Cuyahoga County, Ohio (39035) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0004 | ADVANCED ENERGY INDUSTRIES INC | 2012-03-02 | 08069 | Larimer County, Colorado | Manual point-in-time HQ review: Fort Collins CO 80525 business address assigned to Larimer County for report-only SEC filing-observed address staging. |
| sec_pit_0005 | ADVANCED ENERGY INDUSTRIES INC | 2026-02-13 | 08031 | Denver County, Colorado | Manual point-in-time HQ review: Denver CO 80202 business address assigned to Denver County for report-only SEC filing-observed address staging. |
| sec_pit_0207 | ADVANCED ENERGY INDUSTRIES INC | 2026-05-04 | 08031 | Denver County, Colorado | Manual point-in-time HQ review: Denver CO 80202 business address assigned to Denver County for report-only SEC filing-observed address staging. |
| sec_pit_0281 | Capstone Energy Plus, Inc. | 2011-11-09 | 06037 | Los Angeles County, California | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Los Angeles County, California (06037) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0086 | Capstone Energy Plus, Inc. | 2012-06-14 | 06037 | Los Angeles County, California | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Los Angeles County, California (06037) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0056 | Bimergen Energy Corp | 2009-04-15 | 48201 | Harris County, Texas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Harris County, Texas (48201) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0119 | DEVON ENERGY CORP/DE | 2014-02-28 | 40109 | Oklahoma County, Oklahoma | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Oklahoma County, Oklahoma (40109) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0316 | DEVON ENERGY CORP/DE | 2026-05-06 | 40109 | Oklahoma County, Oklahoma | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Oklahoma County, Oklahoma (40109) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0501 | Allied Energy, Inc. | 2026-05-15 | 34013 | Essex County, New Jersey | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Essex County, New Jersey (34013) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0046 | BUILD-A-BEAR WORKSHOP INC | 2011-03-17 | 29189 | St. Louis County, Missouri | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned St. Louis County, Missouri (29189) for 3 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0047 | BUILD-A-BEAR WORKSHOP INC | 2012-03-15 | 29189 | St. Louis County, Missouri | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned St. Louis County, Missouri (29189) for 3 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0048 | BUILD-A-BEAR WORKSHOP INC | 2013-03-14 | 29189 | St. Louis County, Missouri | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned St. Louis County, Missouri (29189) for 3 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0049 | BUILD-A-BEAR WORKSHOP INC | 2026-04-17 | 29510 | St. Louis city, Missouri | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned St. Louis city, Missouri (29510) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0249 | Big Digital Energy, Inc. | 2008-05-14 | 32510 | Carson City, Nevada | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Carson City, Nevada (32510) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0054 | Big Digital Energy, Inc. | 2009-02-27 | 32510 | Carson City, Nevada | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Carson City, Nevada (32510) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0353 | Energy Transfer LP | 2011-08-08 | 48113 | Dallas County, Texas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Dallas County, Texas (48113) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0154 | Energy Transfer LP | 2012-02-22 | 48113 | Dallas County, Texas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Dallas County, Texas (48113) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0253 | BlackRock Energy & Resources Trust | 2007-05-31 | 36061 | New York County, New York | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned New York County, New York (36061) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0255 | BlackRock Energy & Resources Trust | 2010-10-29 | 36061 | New York County, New York | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned New York County, New York (36061) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0067 | CAMBER ENERGY, INC. | 2008-06-19 | 48201 | Harris County, Texas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Harris County, Texas (48201) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0068 | CAMBER ENERGY, INC. | 2009-03-09 | 48201 | Harris County, Texas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Harris County, Texas (48201) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0069 | CAMBER ENERGY, INC. | 2026-03-30 | 48201 | Harris County, Texas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Harris County, Texas (48201) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0264 | CAMBER ENERGY, INC. | 2026-05-11 | 48201 | Harris County, Texas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Harris County, Texas (48201) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0409 | Tesla, Inc. | 2018-05-07 | 06085 | Santa Clara County, California | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned Santa Clara County, California (06085) for 3 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0200 | Tesla, Inc. | 2019-02-19 | 06085 | Santa Clara County, California | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned Santa Clara County, California (06085) for 3 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0201 | Tesla, Inc. | 2020-02-13 | 06085 | Santa Clara County, California | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned Santa Clara County, California (06085) for 3 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0294 | Clean Energy Technologies, Inc. | 2006-05-17 | 06059 | Orange County, California | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Orange County, California (06059) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0101 | Clean Energy Technologies, Inc. | 2007-04-05 | 06059 | Orange County, California | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Orange County, California (06059) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0292 | Clean Energy Fuels Corp. | 2010-11-08 | 06059 | Orange County, California | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Orange County, California (06059) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0099 | Clean Energy Fuels Corp. | 2011-03-10 | 06059 | Orange County, California | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Orange County, California (06059) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0374 | FORUM ENERGY TECHNOLOGIES, INC. | 2012-05-04 | 48201 | Harris County, Texas | Accepted report-only SEC point-in-time HQ geocode review: residual_same_city_snapshot_county_review assigned Harris County, Texas (48201) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0173 | FORUM ENERGY TECHNOLOGIES, INC. | 2013-03-05 | 48201 | Harris County, Texas | Accepted report-only SEC point-in-time HQ geocode review: residual_same_city_snapshot_county_review assigned Harris County, Texas (48201) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0130 | Data Storage Corp | 2009-03-31 | 36059 | Nassau County, New York | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned Nassau County, New York (36059) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0360 | Enphase Energy, Inc. | 2012-05-14 | 06097 | Sonoma County, California | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned Sonoma County, California (06097) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0159 | Enphase Energy, Inc. | 2013-03-05 | 06097 | Sonoma County, California | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Sonoma County, California (06097) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0236 | BARFRESH FOOD GROUP INC. | 2011-08-19 | 37183 | Wake County, North Carolina | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned Wake County, North Carolina (37183) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0039 | BARFRESH FOOD GROUP INC. | 2012-06-25 | 08031 | Denver County, Colorado | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Denver County, Colorado (08031) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0229 | Amplify Energy Corp. | 2012-06-01 | 48201 | Harris County, Texas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Harris County, Texas (48201) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0030 | Amplify Energy Corp. | 2013-03-21 | 48201 | Harris County, Texas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Harris County, Texas (48201) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0327 | Delek Logistics Partners, LP | 2012-12-14 | 47187 | Williamson County, Tennessee | Accepted report-only SEC point-in-time HQ conflict override: filing-street Census geographies match assigned Williamson County, Tennessee (47187) while the reused current snapshot county differed. Use only for reviewed SEC filing-observed county-year candidates; source promotion remains blocked. |
| sec_pit_0132 | Delek Logistics Partners, LP | 2013-03-12 | 47187 | Williamson County, Tennessee | Accepted report-only SEC point-in-time HQ conflict override: filing-street Census geographies match assigned Williamson County, Tennessee (47187) while the reused current snapshot county differed. Use only for reviewed SEC filing-observed county-year candidates; source promotion remains blocked. |
| sec_pit_0051 | Barrel Energy Inc. | 2022-02-07 | 32003 | Clark County, Nevada | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Clark County, Nevada (32003) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0246 | Barrel Energy Inc. | 2026-05-14 | 32003 | Clark County, Nevada | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Clark County, Nevada (32003) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0257 | Bloom Energy Corp | 2018-09-07 | 06085 | Santa Clara County, California | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Santa Clara County, California (06085) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0163 | Epsilon Energy Ltd. | 2019-03-29 | 48201 | Harris County, Texas | Accepted report-only SEC point-in-time HQ geocode review: residual_same_city_snapshot_county_review assigned Harris County, Texas (48201) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0060 | Blue Star Foods Corp. | 2018-12-31 | 12086 | Miami-Dade County, Florida | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Miami-Dade County, Florida (12086) for 3 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0061 | Blue Star Foods Corp. | 2019-04-01 | 12086 | Miami-Dade County, Florida | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Miami-Dade County, Florida (12086) for 3 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0062 | Blue Star Foods Corp. | 2026-05-22 | 12086 | Miami-Dade County, Florida | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Miami-Dade County, Florida (12086) for 3 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0362 | Eos Energy Enterprises, Inc. | 2020-06-26 | 36061 | New York County, New York | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned New York County, New York (36061) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0156 | Energy Vault Holdings, Inc. | 2021-03-26 | 18097 | Marion County, Indiana | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned Marion County, Indiana (18097) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0158 | Energy Vault Holdings, Inc. | 2026-03-18 | 06111 | Ventura County, California | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:snapshot_street_after_parser_repair assigned Ventura County, California (06111) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0359 | Energy Vault Holdings, Inc. | 2026-05-19 | 06111 | Ventura County, California | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:snapshot_street_after_parser_repair assigned Ventura County, California (06111) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0333 | Dragonfly Energy Holdings Corp. | 2021-09-23 | 36061 | New York County, New York | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned New York County, New York (36061) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0395 | GCT Semiconductor Holding, Inc. | 2021-12-16 | 36061 | New York County, New York | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned New York County, New York (36061) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0186 | GCT Semiconductor Holding, Inc. | 2022-03-18 | 36061 | New York County, New York | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned New York County, New York (36061) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0269 | CHEETAH NET SUPPLY CHAIN SERVICE INC. | 2023-09-05 | 37119 | Mecklenburg County, North Carolina | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Mecklenburg County, North Carolina (37119) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0074 | CHEETAH NET SUPPLY CHAIN SERVICE INC. | 2024-03-18 | 37119 | Mecklenburg County, North Carolina | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Mecklenburg County, North Carolina (37119) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0064 | BranchOut Food Inc. | 2026-03-31 | 41017 | Deschutes County, Oregon | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned Deschutes County, Oregon (41017) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0321 | DT Cloud Star Acquisition Corp | 2024-09-06 | 36047 | Kings County, New York | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parser_repair assigned Kings County, New York (36047) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0126 | DT Cloud Star Acquisition Corp | 2025-03-31 | 36047 | Kings County, New York | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Kings County, New York (36047) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0504 | Alussa Energy Acquisition Corp. II | 2025-11-13 | 48453 | Travis County, Texas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Travis County, Texas (48453) for 1 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0502 | Alussa Energy Acquisition Corp. II | 2025-12-19 | 48453 | Travis County, Texas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Travis County, Texas (48453) for 3 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0421 | Alussa Energy Acquisition Corp. II | 2026-03-27 | 48453 | Travis County, Texas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Travis County, Texas (48453) for 3 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0503 | Alussa Energy Acquisition Corp. II | 2026-05-12 | 48453 | Travis County, Texas | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Travis County, Texas (48453) for 3 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0357 | Energy Transition Special Opportunities | 2025-09-23 | 36061 | New York County, New York | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned New York County, New York (36061) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0358 | Energy Transition Special Opportunities | 2026-02-04 | 36061 | New York County, New York | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned New York County, New York (36061) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0346 | Eagle Nuclear Energy Corp. | 2026-03-02 | 32031 | Washoe County, Nevada | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Washoe County, Nevada (32031) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0347 | Eagle Nuclear Energy Corp. | 2026-04-15 | 32031 | Washoe County, Nevada | Accepted report-only SEC point-in-time HQ geocode review: census_geographies_addressbatch:parsed_original assigned Washoe County, Nevada (32031) for 2 queue row(s). Remains pending SEC source-maturity and promotion gates. |
| sec_pit_0029 | Air Products & Chemicals, Inc. | 2025-11-20 | 42077 | Lehigh County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0228 | Air Products & Chemicals, Inc. | 2026-04-30 | 42077 | Lehigh County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0287 | Cheniere Energy, Inc. | 2015-04-30 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0092 | Cheniere Energy, Inc. | 2016-02-19 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0093 | Cheniere Energy, Inc. | 2026-02-26 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0288 | Cheniere Energy, Inc. | 2026-05-07 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0224 | AUTOMATIC DATA PROCESSING INC | 2018-02-01 | 34013 | Essex County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0023 | AUTOMATIC DATA PROCESSING INC | 2018-08-03 | 34013 | Essex County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0024 | AUTOMATIC DATA PROCESSING INC | 2025-08-06 | 34013 | Essex County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0225 | AUTOMATIC DATA PROCESSING INC | 2026-04-30 | 34013 | Essex County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0044 | BRIDGFORD FOODS CORP | 2003-01-28 | 06059 | Orange County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0066 | CAL-MAINE FOODS INC | 2025-07-22 | 28089 | Madison County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0263 | CAL-MAINE FOODS INC | 2026-04-01 | 28089 | Madison County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0315 | DELTA AIR LINES, INC. | 2026-04-08 | 13121 | Fulton County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0121 | DOLLAR GENERAL CORP | 2014-03-20 | 47037 | Davidson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0122 | DOLLAR GENERAL CORP | 2015-03-20 | 47037 | Davidson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0123 | DOLLAR GENERAL CORP | 2026-03-20 | 47037 | Davidson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0318 | DOLLAR GENERAL CORP | 2026-03-24 | 47037 | Davidson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0341 | EVERSOURCE ENERGY | 2014-11-07 | 25013 | Hampden County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0146 | EVERSOURCE ENERGY | 2015-02-25 | 25013 | Hampden County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0147 | EVERSOURCE ENERGY | 2026-02-17 | 25013 | Hampden County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0342 | EVERSOURCE ENERGY | 2026-05-07 | 25013 | Hampden County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0205 | Walmart Inc. | 2026-03-13 | 05007 | Benton County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0410 | Walmart Inc. | 2026-05-21 | 05007 | Benton County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0081 | CONSUMERS ENERGY CO | 2026-02-10 | 26075 | Jackson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0276 | CONSUMERS ENERGY CO | 2026-04-28 | 26075 | Jackson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0231 | Apple Inc. | 2015-07-22 | 06085 | Santa Clara County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0032 | Apple Inc. | 2015-10-28 | 06085 | Santa Clara County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0033 | Apple Inc. | 2025-10-31 | 06085 | Santa Clara County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0232 | Apple Inc. | 2026-05-01 | 06085 | Santa Clara County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0116 | DATA I/O CORP | 2026-04-30 | 53033 | King County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0312 | DATA I/O CORP | 2026-05-15 | 53033 | King County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0313 | DATA I/O CORP | 2026-05-19 | 53033 | King County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0214 | ALLIANT ENERGY CORP | 2013-11-07 | 55025 | Dane County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0013 | ALLIANT ENERGY CORP | 2014-02-25 | 55025 | Dane County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0014 | ALLIANT ENERGY CORP | 2026-02-20 | 55025 | Dane County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0215 | ALLIANT ENERGY CORP | 2026-05-01 | 55025 | Dane County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0010 | AIR T INC | 2025-08-12 | 37119 | Mecklenburg County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0211 | AIR T INC | 2026-02-13 | 37119 | Mecklenburg County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0319 | DOMINION ENERGY, INC | 2017-11-01 | 51760 | Richmond city | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0124 | DOMINION ENERGY, INC | 2018-02-27 | 51760 | Richmond city | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0125 | DOMINION ENERGY, INC | 2026-02-23 | 51760 | Richmond city | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0320 | DOMINION ENERGY, INC | 2026-05-01 | 51760 | Richmond city | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0401 | MICRON TECHNOLOGY INC | 2017-06-30 | 16001 | Ada County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0192 | MICRON TECHNOLOGY INC | 2017-10-26 | 16001 | Ada County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0193 | MICRON TECHNOLOGY INC | 2025-10-03 | 16001 | Ada County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0402 | MICRON TECHNOLOGY INC | 2026-03-19 | 16001 | Ada County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0399 | HUNT J B TRANSPORT SERVICES INC | 2017-07-28 | 05007 | Benton County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0400 | HUNT J B TRANSPORT SERVICES INC | 2026-04-24 | 05007 | Benton County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0021 | ATMOS ENERGY CORP | 2014-11-06 | 48113 | Dallas County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0022 | ATMOS ENERGY CORP | 2025-11-14 | 48113 | Dallas County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0223 | ATMOS ENERGY CORP | 2026-05-06 | 48113 | Dallas County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0222 | ATMOS ENERGY CORP | 2026-05-06 | 48113 | Dallas County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0212 | ALASKA AIR GROUP, INC. | 2016-05-09 | 53033 | King County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0011 | ALASKA AIR GROUP, INC. | 2017-02-28 | 53033 | King County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0012 | ALASKA AIR GROUP, INC. | 2026-02-12 | 53033 | King County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0213 | ALASKA AIR GROUP, INC. | 2026-05-07 | 53033 | King County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0041 | BLUE DOLPHIN ENERGY CO | 2009-03-13 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0042 | BLUE DOLPHIN ENERGY CO | 2026-03-31 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0239 | BLUE DOLPHIN ENERGY CO | 2026-05-15 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0076 | CMS ENERGY CORP | 2015-02-05 | 26075 | Jackson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0077 | CMS ENERGY CORP | 2026-02-10 | 26075 | Jackson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0271 | CMS ENERGY CORP | 2026-04-28 | 26075 | Jackson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0272 | CMS ENERGY CORP | 2026-05-13 | 26075 | Jackson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0025 | AUTOZONE INC | 2017-10-25 | 47157 | Shelby County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0026 | AUTOZONE INC | 2018-10-24 | 47157 | Shelby County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0027 | AUTOZONE INC | 2025-10-27 | 47157 | Shelby County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0226 | AUTOZONE INC | 2026-03-20 | 47157 | Shelby County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0020 | ASURE SOFTWARE INC | 2026-02-26 | 48453 | Travis County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0220 | ASURE SOFTWARE INC | 2026-04-30 | 48453 | Travis County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0221 | ASURE SOFTWARE INC | 2026-05-13 | 48453 | Travis County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0179 | FUELCELL ENERGY INC | 2025-12-18 | 09190 | Western Connecticut Planning Region | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0377 | FUELCELL ENERGY INC | 2026-03-09 | 09190 | Western Connecticut Planning Region | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0378 | FUELCELL ENERGY INC | 2026-05-21 | 09190 | Western Connecticut Planning Region | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0344 | EXPAND ENERGY Corp | 2026-04-28 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0343 | EXPAND ENERGY Corp | 2026-04-28 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0177 | FORWARD AIR CORP | 2026-03-11 | 48113 | Dallas County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0376 | FORWARD AIR CORP | 2026-05-11 | 48113 | Dallas County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0405 | TRACTOR SUPPLY CO /DE/ | 2013-05-06 | 47187 | Williamson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0196 | TRACTOR SUPPLY CO /DE/ | 2014-02-19 | 47187 | Williamson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0197 | TRACTOR SUPPLY CO /DE/ | 2026-02-19 | 47187 | Williamson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0406 | TRACTOR SUPPLY CO /DE/ | 2026-05-07 | 47187 | Williamson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0337 | ENERGY FOCUS, INC/DE | 2006-08-11 | 39035 | Cuyahoga County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0142 | ENERGY FOCUS, INC/DE | 2007-03-16 | 39035 | Cuyahoga County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0143 | ENERGY FOCUS, INC/DE | 2026-03-24 | 39035 | Cuyahoga County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0208 | ADVANCED ENERGY INDUSTRIES INC | 2026-05-18 | 08031 | Denver County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0277 | COVENANT LOGISTICS GROUP, INC. | 2011-08-12 | 47065 | Hamilton County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0082 | COVENANT LOGISTICS GROUP, INC. | 2012-03-09 | 47065 | Hamilton County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0083 | COVENANT LOGISTICS GROUP, INC. | 2026-02-27 | 47065 | Hamilton County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0278 | COVENANT LOGISTICS GROUP, INC. | 2026-05-07 | 47065 | Hamilton County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0128 | DTE ENERGY CO | 2018-02-16 | 26163 | Wayne County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0129 | DTE ENERGY CO | 2026-02-17 | 26163 | Wayne County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0323 | DTE ENERGY CO | 2026-04-30 | 26163 | Wayne County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0324 | DTE ENERGY CO | 2026-05-15 | 26163 | Wayne County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0087 | Capstone Energy Plus, Inc. | 2025-06-27 | 06037 | Los Angeles County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0282 | Capstone Energy Plus, Inc. | 2026-02-12 | 06037 | Los Angeles County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0006 | AIR INDUSTRIES GROUP | 2008-04-14 | 36103 | Suffolk County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0007 | AIR INDUSTRIES GROUP | 2008-04-17 | 36103 | Suffolk County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0008 | AIR INDUSTRIES GROUP | 2026-03-27 | 36103 | Suffolk County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0209 | AIR INDUSTRIES GROUP | 2026-05-13 | 36103 | Suffolk County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0218 | AMAZON COM INC | 2020-05-01 | 53033 | King County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0017 | AMAZON COM INC | 2021-02-03 | 53033 | King County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0018 | AMAZON COM INC | 2026-02-06 | 53033 | King County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0219 | AMAZON COM INC | 2026-04-30 | 53033 | King County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0397 | GENESIS ENERGY LP | 2012-05-04 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0188 | GENESIS ENERGY LP | 2013-02-26 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0189 | GENESIS ENERGY LP | 2026-02-18 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0398 | GENESIS ENERGY LP | 2026-05-07 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0403 | NVIDIA CORP | 2020-05-21 | 06085 | Santa Clara County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0194 | NVIDIA CORP | 2021-02-26 | 06085 | Santa Clara County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0195 | NVIDIA CORP | 2026-02-25 | 06085 | Santa Clara County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0404 | NVIDIA CORP | 2026-05-20 | 06085 | Santa Clara County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0370 | FEDEX CORP | 2015-03-19 | 47157 | Shelby County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0169 | FEDEX CORP | 2015-07-14 | 47157 | Shelby County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0170 | FEDEX CORP | 2025-07-21 | 47157 | Shelby County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0371 | FEDEX CORP | 2026-03-19 | 47157 | Shelby County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0057 | Bimergen Energy Corp | 2026-03-31 | 06059 | Orange County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0252 | Bimergen Energy Corp | 2026-05-15 | 06059 | Orange County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0391 | GABELLI UTILITY TRUST | 2010-01-22 | 36119 | Westchester County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0392 | GABELLI UTILITY TRUST | 2010-03-31 | 36119 | Westchester County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0393 | GABELLI UTILITY TRUST | 2010-09-21 | 36119 | Westchester County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0394 | GABELLI UTILITY TRUST | 2026-05-07 | 36119 | Westchester County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0317 | DEVON ENERGY CORP/DE | 2026-05-22 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0372 | FLOWERS FOODS INC | 2013-08-13 | 13275 | Thomas County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0171 | FLOWERS FOODS INC | 2014-02-19 | 13275 | Thomas County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0172 | FLOWERS FOODS INC | 2026-02-25 | 13275 | Thomas County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0373 | FLOWERS FOODS INC | 2026-05-21 | 13275 | Thomas County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0070 | CENTERPOINT ENERGY INC | 2015-02-26 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0071 | CENTERPOINT ENERGY INC | 2026-02-19 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0265 | CENTERPOINT ENERGY INC | 2026-04-23 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0266 | CENTERPOINT ENERGY INC | 2026-05-15 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0055 | Big Digital Energy, Inc. | 2026-03-31 | 42007 | Beaver County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0250 | Big Digital Energy, Inc. | 2026-05-14 | 42007 | Beaver County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0155 | Energy Transfer LP | 2026-02-19 | 48113 | Dallas County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0354 | Energy Transfer LP | 2026-05-07 | 48113 | Dallas County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0036 | B&G Foods, Inc. | 2006-03-07 | 34027 | Morris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0037 | B&G Foods, Inc. | 2007-03-08 | 34027 | Morris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0038 | B&G Foods, Inc. | 2026-03-03 | 34027 | Morris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0235 | B&G Foods, Inc. | 2026-05-13 | 34027 | Morris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0387 | GABELLI GLOBAL UTILITY & INCOME TRUST | 2010-01-22 | 36119 | Westchester County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0388 | GABELLI GLOBAL UTILITY & INCOME TRUST | 2010-03-31 | 36119 | Westchester County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0389 | GABELLI GLOBAL UTILITY & INCOME TRUST | 2010-09-21 | 36119 | Westchester County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0390 | GABELLI GLOBAL UTILITY & INCOME TRUST | 2026-05-07 | 36119 | Westchester County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0202 | Tesla, Inc. | 2026-04-30 | 48453 | Travis County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0140 | Duke Energy CORP | 2019-02-28 | 37119 | Mecklenburg County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0141 | Duke Energy CORP | 2026-02-26 | 37119 | Mecklenburg County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0335 | Duke Energy CORP | 2026-05-05 | 37119 | Mecklenburg County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0336 | Duke Energy CORP | 2026-05-13 | 37119 | Mecklenburg County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0102 | Clean Energy Technologies, Inc. | 2025-06-09 | 06059 | Orange County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0295 | Clean Energy Technologies, Inc. | 2025-11-19 | 06059 | Orange County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0153 | Energy Services of America CORP | 2025-12-15 | 54011 | Cabell County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0351 | Energy Services of America CORP | 2026-05-11 | 54011 | Cabell County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0352 | Energy Services of America CORP | 2026-05-21 | 54011 | Cabell County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0100 | Clean Energy Fuels Corp. | 2026-02-24 | 06059 | Orange County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0293 | Clean Energy Fuels Corp. | 2026-05-07 | 06059 | Orange County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0084 | CVR ENERGY INC | 2009-03-13 | 48157 | Fort Bend County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0085 | CVR ENERGY INC | 2026-02-18 | 48157 | Fort Bend County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0279 | CVR ENERGY INC | 2026-04-29 | 48157 | Fort Bend County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0280 | CVR ENERGY INC | 2026-05-12 | 48157 | Fort Bend County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0285 | Cheniere Energy Partners, L.P. | 2007-05-09 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0090 | Cheniere Energy Partners, L.P. | 2008-02-27 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0091 | Cheniere Energy Partners, L.P. | 2026-02-26 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0286 | Cheniere Energy Partners, L.P. | 2026-05-07 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0144 | ENERGY FUELS INC | 2014-03-31 | 08059 | Jefferson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0145 | ENERGY FUELS INC | 2026-02-26 | 08059 | Jefferson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0339 | ENERGY FUELS INC | 2026-05-06 | 08059 | Jefferson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0340 | ENERGY FUELS INC | 2026-05-15 | 08059 | Jefferson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0015 | ALPHA & OMEGA SEMICONDUCTOR Ltd | 2010-09-02 | 06085 | Santa Clara County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0016 | ALPHA & OMEGA SEMICONDUCTOR Ltd | 2025-08-28 | 06085 | Santa Clara County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0174 | FORUM ENERGY TECHNOLOGIES, INC. | 2026-02-27 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0375 | FORUM ENERGY TECHNOLOGIES, INC. | 2026-05-01 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0131 | Data Storage Corp | 2026-04-14 | 36061 | New York County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0326 | Data Storage Corp | 2026-05-15 | 36061 | New York County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0349 | Energy Recovery, Inc. | 2011-11-08 | 06001 | Alameda County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0150 | Energy Recovery, Inc. | 2012-03-14 | 06001 | Alameda County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0151 | Energy Recovery, Inc. | 2026-02-25 | 06001 | Alameda County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0350 | Energy Recovery, Inc. | 2026-05-06 | 06001 | Alameda County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0160 | Enphase Energy, Inc. | 2026-02-17 | 06001 | Alameda County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0361 | Enphase Energy, Inc. | 2026-04-28 | 06001 | Alameda County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0094 | Chord Energy Corp | 2013-03-01 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0095 | Chord Energy Corp | 2014-02-27 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0096 | Chord Energy Corp | 2026-02-26 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0289 | Chord Energy Corp | 2026-05-07 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0040 | BARFRESH FOOD GROUP INC. | 2026-04-15 | 06037 | Los Angeles County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0237 | BARFRESH FOOD GROUP INC. | 2026-05-14 | 06037 | Los Angeles County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0283 | Chefs' Warehouse, Inc. | 2011-09-09 | 09190 | Western Connecticut Planning Region | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0088 | Chefs' Warehouse, Inc. | 2012-03-29 | 09190 | Western Connecticut Planning Region | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0089 | Chefs' Warehouse, Inc. | 2026-02-24 | 09190 | Western Connecticut Planning Region | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0284 | Chefs' Warehouse, Inc. | 2026-04-29 | 09190 | Western Connecticut Planning Region | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0296 | ClearBridge Energy Midstream Opportunity Fund Inc. | 2013-01-28 | 36061 | New York County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0297 | ClearBridge Energy Midstream Opportunity Fund Inc. | 2013-06-14 | 36061 | New York County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0298 | ClearBridge Energy Midstream Opportunity Fund Inc. | 2014-05-29 | 36061 | New York County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0031 | Amplify Energy Corp. | 2026-03-09 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0230 | Amplify Energy Corp. | 2026-05-11 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0329 | Diamondback Energy, Inc. | 2016-05-05 | 48329 | Midland County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0134 | Diamondback Energy, Inc. | 2017-02-15 | 48329 | Midland County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0135 | Diamondback Energy, Inc. | 2026-02-25 | 48329 | Midland County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0330 | Diamondback Energy, Inc. | 2026-05-06 | 48329 | Midland County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0133 | Delek Logistics Partners, LP | 2026-02-27 | 47037 | Davidson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0328 | Delek Logistics Partners, LP | 2026-04-29 | 47037 | Davidson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0300 | Clearway Energy, Inc. | 2016-11-04 | 34021 | Mercer County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0103 | Clearway Energy, Inc. | 2017-02-28 | 34021 | Mercer County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0104 | Clearway Energy, Inc. | 2026-02-24 | 34021 | Mercer County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0301 | Clearway Energy, Inc. | 2026-05-08 | 34021 | Mercer County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0053 | Beyond Air, Inc. | 2025-06-20 | 36059 | Nassau County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0248 | Beyond Air, Inc. | 2026-02-13 | 36059 | Nassau County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0058 | Bloom Energy Corp | 2019-03-22 | 06085 | Santa Clara County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0059 | Bloom Energy Corp | 2026-02-09 | 06085 | Santa Clara County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0258 | Bloom Energy Corp | 2026-04-29 | 06085 | Santa Clara County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0185 | Freight Technologies, Inc. | 2026-05-14 | 48339 | Montgomery County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0114 | Custom Truck One Source, Inc. | 2026-03-10 | 29095 | Jackson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0311 | Custom Truck One Source, Inc. | 2026-04-27 | 29095 | Jackson County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0306 | Construction Partners, Inc. | 2018-06-04 | 01069 | Houston County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0109 | Construction Partners, Inc. | 2018-12-14 | 01069 | Houston County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0110 | Construction Partners, Inc. | 2025-11-25 | 01069 | Houston County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0307 | Construction Partners, Inc. | 2026-05-08 | 01069 | Houston County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0164 | Epsilon Energy Ltd. | 2026-03-27 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0364 | Epsilon Energy Ltd. | 2026-05-13 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0365 | Epsilon Energy Ltd. | 2026-05-20 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0259 | Blue Star Foods Corp. | 2018-05-01 | 12099 | Palm Beach County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0161 | Eos Energy Enterprises, Inc. | 2021-02-26 | 34023 | Middlesex County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0162 | Eos Energy Enterprises, Inc. | 2026-02-26 | 34023 | Middlesex County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0363 | Eos Energy Enterprises, Inc. | 2026-05-13 | 34023 | Middlesex County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0139 | Dragonfly Energy Holdings Corp. | 2026-03-30 | 32031 | Washoe County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0334 | Dragonfly Energy Holdings Corp. | 2026-05-14 | 32031 | Washoe County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0187 | GCT Semiconductor Holding, Inc. | 2026-03-25 | 06085 | Santa Clara County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0396 | GCT Semiconductor Holding, Inc. | 2026-05-12 | 06085 | Santa Clara County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0382 | Fervo Energy Co | 2026-04-17 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0383 | Fervo Energy Co | 2026-05-04 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0384 | Fervo Energy Co | 2026-05-08 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0381 | Fervo Energy Co | 2026-05-15 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0111 | Crescent Energy Co | 2022-03-10 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0112 | Crescent Energy Co | 2026-02-25 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0308 | Crescent Energy Co | 2026-05-04 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0309 | Crescent Energy Co | 2026-05-22 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0302 | Consensus Cloud Solutions, Inc. | 2021-11-15 | 06037 | Los Angeles County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0105 | Consensus Cloud Solutions, Inc. | 2022-04-15 | 06037 | Los Angeles County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0106 | Consensus Cloud Solutions, Inc. | 2026-02-13 | 06037 | Los Angeles County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0303 | Consensus Cloud Solutions, Inc. | 2026-05-08 | 06037 | Los Angeles County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0107 | Constellation Energy Corp | 2022-02-25 | 24510 | Baltimore city | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0108 | Constellation Energy Corp | 2026-02-24 | 24510 | Baltimore city | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0305 | Constellation Energy Corp | 2026-05-11 | 24510 | Baltimore city | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0304 | Constellation Energy Corp | 2026-05-11 | 24510 | Baltimore city | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0180 | Fluence Energy, Inc. | 2021-12-14 | 51013 | Arlington County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0181 | Fluence Energy, Inc. | 2025-11-25 | 51013 | Arlington County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0385 | Fluence Energy, Inc. | 2026-05-06 | 51013 | Arlington County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0386 | Fluence Energy, Inc. | 2026-05-15 | 51013 | Arlington County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0368 | Excelerate Energy, Inc. | 2022-05-26 | 48339 | Montgomery County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0167 | Excelerate Energy, Inc. | 2023-03-29 | 48339 | Montgomery County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0168 | Excelerate Energy, Inc. | 2026-02-27 | 48339 | Montgomery County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0369 | Excelerate Energy, Inc. | 2026-05-07 | 48339 | Montgomery County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0290 | Circle Energy, Inc./NV | 2022-08-08 | 40143 | Tulsa County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0097 | Circle Energy, Inc./NV | 2023-03-29 | 40143 | Tulsa County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0098 | Circle Energy, Inc./NV | 2026-03-24 | 40143 | Tulsa County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0291 | Circle Energy, Inc./NV | 2026-05-11 | 40143 | Tulsa County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0136 | Diversified Energy Co | 2024-03-19 | 01117 | Shelby County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0137 | Diversified Energy Co | 2026-02-26 | 01117 | Shelby County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0331 | Diversified Energy Co | 2026-05-06 | 01117 | Shelby County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0332 | Diversified Energy Co | 2026-05-21 | 01117 | Shelby County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0075 | CHEETAH NET SUPPLY CHAIN SERVICE INC. | 2026-03-20 | 06059 | Orange County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0270 | CHEETAH NET SUPPLY CHAIN SERVICE INC. | 2026-05-14 | 06059 | Orange County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0273 | CO2 Energy Transition Corp. | 2024-12-27 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0078 | CO2 Energy Transition Corp. | 2025-03-31 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0079 | CO2 Energy Transition Corp. | 2026-03-16 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0274 | CO2 Energy Transition Corp. | 2026-05-15 | 48201 | Harris County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0260 | BranchOut Food Inc. | 2023-08-21 | 41017 | Deschutes County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0063 | BranchOut Food Inc. | 2024-04-01 | 41017 | Deschutes County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0261 | BranchOut Food Inc. | 2026-05-14 | 41017 | Deschutes County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0233 | Atlas Energy Solutions Inc. | 2023-10-31 | 48453 | Travis County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0034 | Atlas Energy Solutions Inc. | 2024-02-27 | 48453 | Travis County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0035 | Atlas Energy Solutions Inc. | 2026-02-24 | 48453 | Travis County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0234 | Atlas Energy Solutions Inc. | 2026-05-05 | 48453 | Travis County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0366 | Everus Construction Group, Inc. | 2024-11-21 | 38015 | Burleigh County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0165 | Everus Construction Group, Inc. | 2025-02-28 | 38015 | Burleigh County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0166 | Everus Construction Group, Inc. | 2026-02-25 | 38015 | Burleigh County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0367 | Everus Construction Group, Inc. | 2026-05-06 | 38015 | Burleigh County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0127 | DT Cloud Star Acquisition Corp | 2026-03-25 | 36061 | New York County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0322 | DT Cloud Star Acquisition Corp | 2026-05-08 | 36061 | New York County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0379 | FedEx Freight Holding Company, Inc. | 2026-05-13 | 47157 | Shelby County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0380 | FedEx Freight Holding Company, Inc. | 2026-05-18 | 47157 | Shelby County | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0355 | Energy Transition Special Opportunities | 2026-05-19 | 09190 | Western Connecticut Planning Region | Auto-resolution requires later operator spot-check before source promotion. |
| sec_pit_0356 | Energy Transition Special Opportunities | 2026-05-22 | 09190 | Western Connecticut Planning Region | Auto-resolution requires later operator spot-check before source promotion. |

## County-Year Candidate Preview

| fips | county | year | companies | filings | status |
| --- | --- | ---: | ---: | ---: | --- |
| 06059 | Orange County | 2003 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 28049 | Hinds County, Mississippi | 2003 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 37035 | Catawba County, North Carolina | 2004 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48453 | Travis County, Texas | 2004 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06059 | Orange County, California | 2006 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 34027 | Morris County | 2006 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 39035 | Cuyahoga County | 2006 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06059 | Orange County, California | 2007 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 34027 | Morris County | 2007 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36061 | New York County, New York | 2007 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 39035 | Cuyahoga County | 2007 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County | 2007 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 32510 | Carson City, Nevada | 2008 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36103 | Suffolk County | 2008 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County | 2008 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County, Texas | 2008 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 32510 | Carson City, Nevada | 2009 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36059 | Nassau County, New York | 2009 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48157 | Fort Bend County | 2009 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County | 2009 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County, Texas | 2009 | 2 | 2 | report_only_candidate_pending_source_maturity_gate |
| 06059 | Orange County, California | 2010 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06085 | Santa Clara County | 2010 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36061 | New York County, New York | 2010 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36119 | Westchester County | 2010 | 2 | 6 | report_only_candidate_pending_source_maturity_gate |
| 06001 | Alameda County | 2011 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06037 | Los Angeles County, California | 2011 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06059 | Orange County, California | 2011 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 09190 | Western Connecticut Planning Region | 2011 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 29189 | St. Louis County, Missouri | 2011 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 37183 | Wake County, North Carolina | 2011 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 47065 | Hamilton County | 2011 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48113 | Dallas County, Texas | 2011 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06001 | Alameda County | 2012 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06037 | Los Angeles County, California | 2012 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06097 | Sonoma County, California | 2012 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 08031 | Denver County, Colorado | 2012 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 08069 | Larimer County, Colorado | 2012 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 09001 | Fairfield County, Connecticut | 2012 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 09190 | Western Connecticut Planning Region | 2012 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 29189 | St. Louis County, Missouri | 2012 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 47065 | Hamilton County | 2012 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 47187 | Williamson County, Tennessee | 2012 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48113 | Dallas County, Texas | 2012 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County | 2012 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County, Texas | 2012 | 2 | 2 | report_only_candidate_pending_source_maturity_gate |
| 06097 | Sonoma County, California | 2013 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 13275 | Thomas County | 2013 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 29189 | St. Louis County, Missouri | 2013 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36061 | New York County | 2013 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 47187 | Williamson County | 2013 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 47187 | Williamson County, Tennessee | 2013 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County | 2013 | 2 | 2 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County, Texas | 2013 | 2 | 2 | report_only_candidate_pending_source_maturity_gate |
| 55025 | Dane County | 2013 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 05143 | Washington County, Arkansas | 2014 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 08059 | Jefferson County | 2014 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 13275 | Thomas County | 2014 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 25013 | Hampden County | 2014 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36061 | New York County | 2014 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 40109 | Oklahoma County, Oklahoma | 2014 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 47037 | Davidson County | 2014 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 47187 | Williamson County | 2014 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48113 | Dallas County | 2014 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County | 2014 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 55025 | Dane County | 2014 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06085 | Santa Clara County | 2015 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 25013 | Hampden County | 2015 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 26075 | Jackson County | 2015 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 47037 | Davidson County | 2015 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 47059 | Greene County, Tennessee | 2015 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 47157 | Shelby County | 2015 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County | 2015 | 2 | 2 | report_only_candidate_pending_source_maturity_gate |
| 34021 | Mercer County | 2016 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 40109 | Oklahoma County, Oklahoma | 2016 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 42077 | Lehigh County, Pennsylvania | 2016 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 47059 | Greene County, Tennessee | 2016 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County | 2016 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48329 | Midland County | 2016 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 53033 | King County | 2016 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 05007 | Benton County | 2017 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 16001 | Ada County | 2017 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 34021 | Mercer County | 2017 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 47157 | Shelby County | 2017 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48329 | Midland County | 2017 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 51760 | Richmond city | 2017 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 53033 | King County | 2017 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 01069 | Houston County | 2018 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 06085 | Santa Clara County, California | 2018 | 2 | 2 | report_only_candidate_pending_source_maturity_gate |
| 12086 | Miami-Dade County, Florida | 2018 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 12099 | Palm Beach County | 2018 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 26163 | Wayne County | 2018 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 34013 | Essex County | 2018 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 47157 | Shelby County | 2018 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 51760 | Richmond city | 2018 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06085 | Santa Clara County | 2019 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06085 | Santa Clara County, California | 2019 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 12086 | Miami-Dade County, Florida | 2019 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 37119 | Mecklenburg County | 2019 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County, Texas | 2019 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06085 | Santa Clara County | 2020 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06085 | Santa Clara County, California | 2020 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36061 | New York County, New York | 2020 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 53033 | King County | 2020 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06037 | Los Angeles County | 2021 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06085 | Santa Clara County | 2021 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 18097 | Marion County, Indiana | 2021 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 34023 | Middlesex County | 2021 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36061 | New York County, New York | 2021 | 2 | 2 | report_only_candidate_pending_source_maturity_gate |
| 51013 | Arlington County | 2021 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 53033 | King County | 2021 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06037 | Los Angeles County | 2022 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 24510 | Baltimore city | 2022 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 32003 | Clark County, Nevada | 2022 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36061 | New York County, New York | 2022 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 40143 | Tulsa County | 2022 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County | 2022 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48339 | Montgomery County | 2022 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 37119 | Mecklenburg County, North Carolina | 2023 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 40143 | Tulsa County | 2023 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 41017 | Deschutes County | 2023 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48339 | Montgomery County | 2023 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48453 | Travis County | 2023 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 01117 | Shelby County | 2024 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36047 | Kings County, New York | 2024 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 37119 | Mecklenburg County, North Carolina | 2024 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 38015 | Burleigh County | 2024 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 41017 | Deschutes County | 2024 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County | 2024 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48453 | Travis County | 2024 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 01069 | Houston County | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 05143 | Washington County, Arkansas | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06037 | Los Angeles County | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06059 | Orange County | 2025 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 06085 | Santa Clara County | 2025 | 2 | 2 | report_only_candidate_pending_source_maturity_gate |
| 09190 | Western Connecticut Planning Region | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 16001 | Ada County | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 28089 | Madison County | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 34013 | Essex County | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36047 | Kings County, New York | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36059 | Nassau County | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36061 | New York County, New York | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 37119 | Mecklenburg County | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 38015 | Burleigh County | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 42077 | Lehigh County | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 47157 | Shelby County | 2025 | 2 | 2 | report_only_candidate_pending_source_maturity_gate |
| 48113 | Dallas County | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 48453 | Travis County, Texas | 2025 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 51013 | Arlington County | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 54011 | Cabell County | 2025 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 01069 | Houston County | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 01117 | Shelby County | 2026 | 1 | 3 | report_only_candidate_pending_source_maturity_gate |
| 05007 | Benton County | 2026 | 2 | 3 | report_only_candidate_pending_source_maturity_gate |
| 05143 | Washington County, Arkansas | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 06001 | Alameda County | 2026 | 2 | 4 | report_only_candidate_pending_source_maturity_gate |
| 06037 | Los Angeles County | 2026 | 3 | 5 | report_only_candidate_pending_source_maturity_gate |
| 06059 | Orange County | 2026 | 3 | 6 | report_only_candidate_pending_source_maturity_gate |
| 06085 | Santa Clara County | 2026 | 4 | 7 | report_only_candidate_pending_source_maturity_gate |
| 06111 | Ventura County, California | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 08031 | Denver County | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 08031 | Denver County, Colorado | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 08059 | Jefferson County | 2026 | 1 | 3 | report_only_candidate_pending_source_maturity_gate |
| 09190 | Western Connecticut Planning Region | 2026 | 3 | 6 | report_only_candidate_pending_source_maturity_gate |
| 10003 | New Castle County, Delaware | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 12086 | Miami-Dade County, Florida | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 13121 | Fulton County | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 13275 | Thomas County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 16001 | Ada County | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 24510 | Baltimore city | 2026 | 1 | 3 | report_only_candidate_pending_source_maturity_gate |
| 25013 | Hampden County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 26075 | Jackson County | 2026 | 2 | 3 | report_only_candidate_pending_source_maturity_gate |
| 26163 | Wayne County | 2026 | 1 | 3 | report_only_candidate_pending_source_maturity_gate |
| 28089 | Madison County | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 29095 | Jackson County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 29510 | St. Louis city, Missouri | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 32003 | Clark County, Nevada | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 32031 | Washoe County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 32031 | Washoe County, Nevada | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 34013 | Essex County | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 34013 | Essex County, New Jersey | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 34021 | Mercer County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 34023 | Middlesex County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 34027 | Morris County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 36059 | Nassau County | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36061 | New York County | 2026 | 2 | 4 | report_only_candidate_pending_source_maturity_gate |
| 36061 | New York County, New York | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 36103 | Suffolk County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 36119 | Westchester County | 2026 | 2 | 2 | report_only_candidate_pending_source_maturity_gate |
| 37119 | Mecklenburg County | 2026 | 2 | 4 | report_only_candidate_pending_source_maturity_gate |
| 38015 | Burleigh County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 39035 | Cuyahoga County | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 39035 | Cuyahoga County, Ohio | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 40109 | Oklahoma County, Oklahoma | 2026 | 2 | 2 | report_only_candidate_pending_source_maturity_gate |
| 40143 | Tulsa County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 41017 | Deschutes County | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 41017 | Deschutes County, Oregon | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 42007 | Beaver County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 42077 | Lehigh County | 2026 | 1 | 1 | report_only_candidate_pending_source_maturity_gate |
| 47037 | Davidson County | 2026 | 2 | 4 | report_only_candidate_pending_source_maturity_gate |
| 47065 | Hamilton County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 47157 | Shelby County | 2026 | 3 | 4 | report_only_candidate_pending_source_maturity_gate |
| 47187 | Williamson County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 48113 | Dallas County | 2026 | 3 | 6 | report_only_candidate_pending_source_maturity_gate |
| 48157 | Fort Bend County | 2026 | 1 | 3 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County | 2026 | 14 | 32 | report_only_candidate_pending_source_maturity_gate |
| 48201 | Harris County, Texas | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 48329 | Midland County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 48339 | Montgomery County | 2026 | 2 | 3 | report_only_candidate_pending_source_maturity_gate |
| 48453 | Travis County | 2026 | 3 | 6 | report_only_candidate_pending_source_maturity_gate |
| 48453 | Travis County, Texas | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 51013 | Arlington County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 51760 | Richmond city | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 53033 | King County | 2026 | 3 | 7 | report_only_candidate_pending_source_maturity_gate |
| 54011 | Cabell County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |
| 55025 | Dane County | 2026 | 1 | 2 | report_only_candidate_pending_source_maturity_gate |

## Decision

- `point_in_time_address_geocode_review_applied_keep_report_only`.
- Next action: Rerun SEC source maturity and decide whether to extend the filing parse batch before any source-promotion review.

## Boundary

- This is a report-only source artifact.
- It does not change model features, scoring, ranks, Product Mode policy, source promotion, or feature eligibility.
