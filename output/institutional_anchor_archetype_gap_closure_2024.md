# Institutional Anchor Archetype Gap Closure

## TLDR

- Status: `report_only_college_medical_archetype_gap_closure_ready`.
- Production model/rank/dashboard change: `False`.
- Eligible gap-closure rows: `448`.
- Export rows: `100`.
- Decision: Use official institutional-anchor scores to fill the college/medical archetype review gap in report-only pre-boom queues.

## Top Review Rows

| Rank | County | Score | IPEDS Enrollment | CMS Beds | Primary Archetype |
|---:|---|---:|---:|---:|---|
| 1 | Los Angeles County, California, CA | 100.0 | 972425 | 12878 | manufacturing reshoring |
| 2 | Cook County, Illinois, IL | 99.9 | 368309 | 5637 | amenity migration |
| 3 | Harris County, Texas, TX | 99.7 | 267187 | 7066 | manufacturing reshoring |
| 4 | New York County, New York, NY | 99.6 | 333567 | 5858 | manufacturing reshoring |
| 5 | Tarrant County, Texas, TX | 99.3 | 150398 | 3708 | amenity migration |
| 6 | Maricopa County, Arizona, AZ | 99.2 | 734918 | 6934 | remote-work lifestyle market |
| 7 | Marion County, Indiana, IN | 99.1 | 231716 | 3310 | amenity migration |
| 8 | Wayne County, Michigan, MI | 98.9 | 99807 | 2390 | amenity migration |
| 9 | Middlesex County, Massachusetts, MA | 98.9 | 150651 | 1809 | manufacturing reshoring |
| 10 | Suffolk County, Massachusetts, MA | 98.8 | 189705 | 5562 | manufacturing reshoring |
| 11 | San Diego County, California, CA | 98.8 | 416559 | 4145 | remote-work lifestyle market |
| 12 | Clark County, Nevada, NV | 98.6 | 101342 | 1930 | remote-work lifestyle market |
| 13 | Nassau County, New York, NY | 98.5 | 81323 | 2342 | manufacturing reshoring |
| 14 | San Bernardino County, California, CA | 98.4 | 128616 | 1778 | remote-work lifestyle market |
| 15 | Hennepin County, Minnesota, MN | 98.4 | 247960 | 3362 | amenity migration |
| 16 | King County, Washington, WA | 98.3 | 164503 | 2062 | manufacturing reshoring |
| 17 | St. Louis County, Missouri, MO | 98.3 | 92658 | 3795 | amenity migration |
| 18 | Riverside County, California, CA | 98.2 | 156165 | 1409 | remote-work lifestyle market |
| 19 | Salt Lake County, Utah, UT | 98.2 | 337284 | 1709 | remote-work lifestyle market |
| 20 | Dallas County, Texas, TX | 98.1 | 191234 | 2330 | amenity migration |

## Boundary

- This closes an operator-review archetype gap only.
- Do not use these scores in production models, default ranks, or source promotion until institutional source-maturity and leakage gates pass.
