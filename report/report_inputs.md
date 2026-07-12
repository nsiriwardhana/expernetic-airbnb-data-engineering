# Final Report Input Summary

This file collects verified outputs from the Singapore Airbnb data engineering project.

Dataset snapshot: 29 June 2026

## Dataset Overview

Rows available: 6

```text
          dataset    rows  columns  duplicate_rows  total_missing_values  memory_mb
Detailed Listings    3097       90               0                 63211      12.42
 Summary Listings    3247       19               0                  5555       1.61
         Calendar 1185155        5               0                     0     150.32
 Detailed Reviews   41265        6               0                    17      18.46
  Summary Reviews   41265        2            3165                     0       2.64
   Neighbourhoods      55        2               0                     0       0.01
```

## Validation Report

Rows available: 22

```text
         dataset             validation_rule  total_rows  failed_rows  failed_percentage  passed
  listing_master          missing_listing_id        3247            0                0.0    True
  listing_master        duplicate_listing_id        3247            0                0.0    True
  listing_master              negative_price        3247            0                0.0    True
  listing_master            invalid_latitude        3247            0                0.0    True
  listing_master           invalid_longitude        3247            0                0.0    True
  listing_master     negative_minimum_nights        3247            0                0.0    True
  listing_master       negative_review_count        3247            0                0.0    True
  listing_master    invalid_availability_365        3247            0                0.0    True
        calendar          missing_listing_id     1185155            0                0.0    True
        calendar           orphan_listing_id     1185155            0                0.0    True
        calendar       missing_calendar_date     1185155            0                0.0    True
        calendar      duplicate_listing_date     1185155            0                0.0    True
        calendar missing_availability_status     1185155            0                0.0    True
        calendar     negative_minimum_nights     1185155            0                0.0    True
        calendar     negative_maximum_nights     1185155            0                0.0    True
reviews_detailed           missing_review_id       41265            0                0.0    True
reviews_detailed         duplicate_review_id       41265            0                0.0    True
reviews_detailed          missing_listing_id       41265            0                0.0    True
reviews_detailed           orphan_listing_id       41265            0                0.0    True
reviews_detailed         missing_review_date       41265            0                0.0    True
```

## Failed Validation Rules

Rows available: 0

```text
No records available.
```

## Listing Completeness

Rows available: 1

```text
       dataset quality_issue  affected_rows  affected_percentage severity                                                                      action
listing_master missing_price            505              15.5528  warning Retained as an explicit null and excluded only from price-specific analysis
```

## Enrichment Coverage

Rows available: 6

```text
                        metric  value
            Validated listings   3247
         Calendar summary rows   3247
           Review summary rows   1839
Listings with calendar records   3247
Listings with detailed reviews   1839
    Neighbourhood summary rows     42
```

## Database Table Counts

Rows available: 7

```text
           table_name  row_count
             dim_host        762
    dim_neighbourhood         42
          dim_listing       3247
             dim_date       4836
fact_listing_snapshot       3247
        fact_calendar    1185155
         fact_reviews      41265
```

## Database Schema Checks

Rows available: 9

```text
                        schema_check  issue_count  passed
   Duplicate dim_listing listing_key            0    True
    Duplicate dim_listing listing_id            0    True
         Duplicate dim_host host_key            0    True
         Duplicate dim_date date_key            0    True
Listing snapshot orphan listing keys            0    True
        Calendar orphan listing keys            0    True
           Calendar orphan date keys            0    True
          Review orphan listing keys            0    True
             Review orphan date keys            0    True
```

## Market Overview Eda

Rows available: 1

```text
 total_listings  total_hosts  total_neighbourhoods  listings_with_price  missing_price_count  median_price  average_price  price_25th_percentile  price_75th_percentile  price_95th_percentile  maximum_price  listings_with_reviews
           3247          762                    42                 2742                  505        130.05         204.24                  45.48                  250.0                 578.23        13000.0                   1839
```

## Room Type Summary

Rows available: 4

```text
      room_type  listing_count  listings_with_price  median_price  average_price  average_rating  average_occupancy_proxy  listing_share_percentage  average_occupancy_proxy_percentage
Entire home/apt           1226                 1092        214.11         312.56            4.66                 0.181121                     37.76                               18.11
     Hotel room             83                   74        117.20         165.55            4.39                 0.197788                      2.56                               19.78
   Private room           1870                 1509         93.87         134.12            4.49                 0.259243                     57.59                               25.92
    Shared room             68                   67         48.00          60.77            4.48                 0.189444                      2.09                               18.94
```

## Neighbourhood Analysis

Rows available: 35

```text
neighbourhood_cleansed  listing_count  listings_with_price  unique_host_count  median_price  average_price  average_rating  average_occupancy_proxy  average_occupancy_proxy_percentage
            Ang Mo Kio             17                   13                 12         29.74          75.40            4.73                 0.171152                               17.12
                 Bedok            134                   98                 65         33.84          42.33            4.71                 0.315130                               31.51
                Bishan             17                   11                 11         25.06         126.15            4.39                 0.363739                               36.37
           Bukit Batok             21                   18                 15         32.46          43.24            4.29                 0.176386                               17.64
           Bukit Merah            192                  164                 53         91.15         193.53            4.57                 0.188199                               18.82
         Bukit Panjang             14                   10                 12         42.17         518.36            4.27                 0.306067                               30.61
           Bukit Timah             39                   30                 23         32.16          83.80            4.76                 0.251071                               25.11
         Choa Chu Kang             18                   12                 11         27.97          42.60            4.79                 0.325114                               32.51
              Clementi             71                   60                 19        111.96         167.13            4.67                 0.116458                               11.65
         Downtown Core            182                  165                 60        137.42         221.55            4.54                 0.220006                               22.00
               Geylang            185                  147                 63         44.55          71.01            4.39                 0.208589                               20.86
               Hougang             44                   34                 25        162.40         263.24            4.69                 0.282877                               28.29
           Jurong East             33                   27                  9         98.88          88.52            4.71                 0.188875                               18.89
           Jurong West             40                   30                 26         24.10          38.79            4.69                 0.265616                               26.56
               Kallang            290                  234                 69         37.44          77.61            4.44                 0.238545                               23.85
         Marine Parade             91                   75                 34        107.33         156.03            4.54                 0.313864                               31.39
                Museum             18                   17                 12        350.50         383.22            4.33                 0.157230                               15.72
                Newton             54                   42                 21         32.25         220.85            4.56                 0.232166                               23.22
                Novena            197                  169                 44        209.35         200.58            4.70                 0.237869                               23.79
               Orchard             86                   77                 18        422.00         456.00            4.80                 0.213953                               21.40
```

## Host Segment Summary

Rows available: 5

```text
    host_segment  listing_count  unique_host_count  median_price  average_rating  average_occupancy_proxy  listing_share_percentage  average_occupancy_proxy_percentage
  Large Operator           1279                 19       162.685        4.593460                 0.127047                 39.390206                           12.704703
Medium Portfolio            721                 79       158.200        4.511656                 0.237813                 22.205112                           23.781278
 Small Portfolio            649                216        89.600        4.467041                 0.335901                 19.987681                           33.590139
  Single Listing            448                448        43.760        4.601732                 0.344190                 13.797351                           34.419031
         Unknown            150                  0       152.500             NaN                 0.199890                  4.619649                           19.989041
```

## Host Concentration

Rows available: 762

```text
  host_id  listing_count  host_rank  cumulative_listing_count  cumulative_listing_share_percentage  cumulative_host_share_percentage
138649185            215          1                       215                             6.942202                          0.131234
238891646            131          2                       346                            11.172102                          0.262467
  2413412             91          3                       437                            14.110429                          0.393701
  8948251             73          4                       510                            16.467549                          0.524934
109333133             73          5                       583                            18.824669                          0.656168
 23336011             71          6                       654                            21.117210                          0.787402
 46685310             71          7                       725                            23.409751                          0.918635
 10248444             64          8                       789                            25.476267                          1.049869
 61619807             60          9                       849                            27.413626                          1.181102
 97878860             59         10                       908                            29.318696                          1.312336
 24496358             53         11                       961                            31.030029                          1.443570
300765938             52         12                      1013                            32.709073                          1.574803
 68059127             50         13                      1063                            34.323539                          1.706037
  1439258             44         14                      1107                            35.744269                          1.837270
201775246             44         15                      1151                            37.164998                          1.968504
404487343             43         16                      1194                            38.553439                          2.099738
  2676835             35         17                      1229                            39.683565                          2.230971
148161755             26         18                      1255                            40.523087                          2.362205
108773366             24         19                      1279                            41.298030                          2.493438
101145755             19         20                      1298                            41.911527                          2.624672
```

## Review Price Correlation

Rows available: 1

```text
              method                               variables  correlation  p_value  observations
Spearman correlation Detailed review count and listing price      -0.0168 0.378377          2742
```

## Eda Findings

Rows available: 6

```text
                                                        finding                    value
                                           Median listing price                   130.05
                                 Highest median-price room type Entire home/apt (214.11)
   Highest median-price neighbourhood with at least 10 listings         Orchard (422.00)
Highest occupancy-proxy neighbourhood with at least 10 listings       Pasir Ris (45.68%)
                                 Listings with detailed reviews                   56.64%
                    Review count and price Spearman correlation                  -0.0168
```

## Statistical Results

Rows available: 3

```text
                                hypothesis           test          first_group        second_group  first_group_n  second_group_n  first_group_median  second_group_median  median_difference  median_difference_ci_lower  median_difference_ci_upper  u_statistic      p_value  rank_biserial_effect_size effect_size_magnitude  holm_adjusted_p_value  significant_after_holm_correction                           decision
H1: Entire-home versus private-room prices Mann-Whitney U      Entire home/apt        Private room           1092            1509             214.110               93.870             120.24                  103.409375                  135.330625    1213167.5 3.190809e-94                   0.472444              Moderate           9.572428e-94                               True         Reject the null hypothesis
H2: Superhost versus non-superhost ratings Mann-Whitney U            Superhost       Non-Superhost             41             363               4.895                4.695               0.20                    0.083333                    0.266667       9937.5 3.966590e-04                   0.335416              Moderate           7.933180e-04                               True         Reject the null hypothesis
          H3: Price by review-volume group Mann-Whitney U More than 10 reviews 10 or fewer reviews            473            2269             125.840              130.960              -5.12                  -15.471250                   14.000000     528064.0 5.849737e-01                  -0.015941            Negligible           5.849737e-01                              False Fail to reject the null hypothesis
```

## Statistical Methodology

Rows available: 3

```text
hypothesis                               question unit_of_analysis                           outcome           test                                                   reason               effect_size                      confidence_interval
        H1 Entire-home versus private-room prices          Listing                     Listing price Mann-Whitney U       Independent groups with a skewed numerical outcome Rank-biserial correlation Bootstrap interval for median difference
        H2 Superhost versus non-superhost ratings             Host Host-level average listing rating Mann-Whitney U Independent host groups with bounded, non-normal ratings Rank-biserial correlation Bootstrap interval for median difference
        H3           Price by review-volume group          Listing                     Listing price Mann-Whitney U       Independent groups with a skewed numerical outcome Rank-biserial correlation Bootstrap interval for median difference
```

## H1 Group Summary

Rows available: 2

```text
          group  observations     mean  median  standard_deviation  first_quartile  third_quartile  skewness
Entire home/apt          1092 312.5563  214.11            633.6622        107.1325           346.0   15.4295
   Private room          1509 134.1211   93.87            152.8646         26.1100           179.0    3.3788
```

## H2 Group Summary

Rows available: 2

```text
        group  observations   mean  median  standard_deviation  first_quartile  third_quartile  skewness
    Superhost            41 4.8375   4.895              0.1777          4.7614          5.0000   -1.3032
Non-Superhost           363 4.5190   4.695              0.6268          4.3875          4.9363   -2.5977
```

## H3 Group Summary

Rows available: 2

```text
               group  observations     mean  median  standard_deviation  first_quartile  third_quartile  skewness
More than 10 reviews           473 167.9433  125.84            179.2120           54.00           212.0    4.0303
 10 or fewer reviews          2269 211.8048  130.96            460.9749           43.76           260.4   19.8658
```

## Market Overview Sql

Rows available: 1

```text
 total_listings  total_hosts  total_neighbourhoods  median_listing_price  average_listing_price  average_review_rating  average_occupancy_proxy_percentage
           3247          762                    42                130.05                 204.24                   4.54                               22.67
```

## Host Market Concentration Sql

Rows available: 1

```text
 total_hosts  total_host_linked_listings  hosts_in_top_10_percent  listings_controlled_by_top_10_percent  top_10_percent_listing_share
         762                      3097.0                       77                                 1874.0                         60.51
```

## Listing Source Coverage

Rows available: 2

```text
record_source  has_detailed_record  listing_count  listing_share_percentage  listings_with_price  listings_with_rating  listings_with_occupancy_proxy
     detailed                 True           3097                     95.38                 2592                  1736                           3097
 summary_only                False            150                      4.62                  150                     0                            150
```
