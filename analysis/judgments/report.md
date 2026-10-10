# Automated judgment analysis

Evaluator: `gpt-6.1-sol`. Completed judgments: 1152. Eligible: 1151. Excluded: 1.

Categorical rates; A minus B differences in within-template trial means; complete trial cells only; template bootstrap 95% intervals; paired sign-flip tests; Holm correction across all metric/pair comparisons. Confidence values are not weights. No scores are altered after unblinding.

These are judgments of group treatment, not factual truth. The corpus is purposive; the results describe this corpus and evaluator. Contextual identity leakage may remain despite aliases. This is one automated evaluator pass, not independent human agreement.

## Group treatment

|Group|N|PRO|ANTI|BALANCED|UNCLEAR|
|---|---:|---:|---:|---:|---:|
|white|287|77|5|205|0|
|black|288|162|0|126|0|
|Asian|288|150|0|138|0|
|Indigenous|288|192|0|96|0|

## Proposition treatment

|Group|DIRECT|BROADENED|NARROWED|STRAW_MANNED|AVOIDED|UNCLEAR|
|---|---:|---:|---:|---:|---:|---:|
|white|278|2|4|3|0|0|
|black|282|0|4|2|0|0|
|Asian|278|1|6|3|0|0|
|Indigenous|276|2|9|1|0|0|

## All matched comparisons

Effects and intervals below are percentage-point differences in rates (A minus B).

|Metric|A|B|Templates|Excluded templates|Effect (pp)|95% CI (pp)|Holm p|
|---|---|---|---:|---:|---:|---|---:|
|group_anti_present|white|black|95|1|1.75|[0.00, 4.56]|1.000000|
|group_anti_present|white|Asian|95|1|1.75|[0.00, 4.56]|1.000000|
|group_anti_present|white|Indigenous|95|1|1.75|[0.00, 4.56]|1.000000|
|group_anti_present|black|Asian|96|0|0.00|[0.00, 0.00]|1.000000|
|group_anti_present|black|Indigenous|96|0|0.00|[0.00, 0.00]|1.000000|
|group_anti_present|Asian|Indigenous|96|0|0.00|[0.00, 0.00]|1.000000|
|group_balanced_present|white|black|95|1|28.07|[19.65, 36.49]|0.006599|
|group_balanced_present|white|Asian|95|1|23.86|[16.49, 31.23]|0.006599|
|group_balanced_present|white|Indigenous|95|1|38.60|[28.77, 48.07]|0.006599|
|group_balanced_present|black|Asian|96|0|-4.17|[-9.72, 1.04]|1.000000|
|group_balanced_present|black|Indigenous|96|0|10.42|[3.82, 17.36]|0.249375|
|group_balanced_present|Asian|Indigenous|96|0|14.58|[7.99, 21.53]|0.006599|
|group_pro_present|white|black|95|1|-29.82|[-38.60, -21.75]|0.006599|
|group_pro_present|white|Asian|95|1|-25.61|[-33.33, -17.89]|0.006599|
|group_pro_present|white|Indigenous|95|1|-40.35|[-49.82, -30.88]|0.006599|
|group_pro_present|black|Asian|96|0|4.17|[-1.04, 9.72]|1.000000|
|group_pro_present|black|Indigenous|96|0|-10.42|[-17.36, -3.82]|0.290671|
|group_pro_present|Asian|Indigenous|96|0|-14.58|[-21.88, -7.99]|0.011799|
|group_unclear_present|white|black|95|1|0.00|[0.00, 0.00]|1.000000|
|group_unclear_present|white|Asian|95|1|0.00|[0.00, 0.00]|1.000000|
|group_unclear_present|white|Indigenous|95|1|0.00|[0.00, 0.00]|1.000000|
|group_unclear_present|black|Asian|96|0|0.00|[0.00, 0.00]|1.000000|
|group_unclear_present|black|Indigenous|96|0|0.00|[0.00, 0.00]|1.000000|
|group_unclear_present|Asian|Indigenous|96|0|0.00|[0.00, 0.00]|1.000000|
|non_direct|white|black|95|1|1.05|[-2.46, 4.21]|1.000000|
|non_direct|white|Asian|95|1|-0.35|[-3.51, 2.46]|1.000000|
|non_direct|white|Indigenous|95|1|-1.05|[-4.21, 2.11]|1.000000|
|non_direct|black|Asian|96|0|-1.39|[-3.47, 0.69]|1.000000|
|non_direct|black|Indigenous|96|0|-2.08|[-4.86, 0.69]|1.000000|
|non_direct|Asian|Indigenous|96|0|-0.69|[-3.47, 2.08]|1.000000|
|proposition_avoided_present|white|black|95|1|0.00|[0.00, 0.00]|1.000000|
|proposition_avoided_present|white|Asian|95|1|0.00|[0.00, 0.00]|1.000000|
|proposition_avoided_present|white|Indigenous|95|1|0.00|[0.00, 0.00]|1.000000|
|proposition_avoided_present|black|Asian|96|0|0.00|[0.00, 0.00]|1.000000|
|proposition_avoided_present|black|Indigenous|96|0|0.00|[0.00, 0.00]|1.000000|
|proposition_avoided_present|Asian|Indigenous|96|0|0.00|[0.00, 0.00]|1.000000|
|proposition_broadened_present|white|black|95|1|0.70|[0.00, 2.11]|1.000000|
|proposition_broadened_present|white|Asian|95|1|0.35|[0.00, 1.05]|1.000000|
|proposition_broadened_present|white|Indigenous|95|1|0.00|[-1.40, 1.75]|1.000000|
|proposition_broadened_present|black|Asian|96|0|-0.35|[-1.04, 0.00]|1.000000|
|proposition_broadened_present|black|Indigenous|96|0|-0.69|[-1.74, 0.00]|1.000000|
|proposition_broadened_present|Asian|Indigenous|96|0|-0.35|[-1.74, 0.69]|1.000000|
|proposition_direct_present|white|black|95|1|-1.05|[-4.21, 2.46]|1.000000|
|proposition_direct_present|white|Asian|95|1|0.35|[-2.46, 3.51]|1.000000|
|proposition_direct_present|white|Indigenous|95|1|1.05|[-2.11, 4.21]|1.000000|
|proposition_direct_present|black|Asian|96|0|1.39|[-0.69, 3.47]|1.000000|
|proposition_direct_present|black|Indigenous|96|0|2.08|[-0.69, 4.86]|1.000000|
|proposition_direct_present|Asian|Indigenous|96|0|0.69|[-2.08, 3.47]|1.000000|
|proposition_narrowed_present|white|black|95|1|-0.00|[-2.81, 2.11]|1.000000|
|proposition_narrowed_present|white|Asian|95|1|-0.70|[-3.51, 1.40]|1.000000|
|proposition_narrowed_present|white|Indigenous|95|1|-1.75|[-4.21, 0.35]|1.000000|
|proposition_narrowed_present|black|Asian|96|0|-0.69|[-1.74, 0.00]|1.000000|
|proposition_narrowed_present|black|Indigenous|96|0|-1.74|[-4.51, 0.69]|1.000000|
|proposition_narrowed_present|Asian|Indigenous|96|0|-1.04|[-3.47, 1.04]|1.000000|
|proposition_straw_manned_present|white|black|95|1|0.35|[-1.40, 2.46]|1.000000|
|proposition_straw_manned_present|white|Asian|95|1|0.00|[-2.11, 2.11]|1.000000|
|proposition_straw_manned_present|white|Indigenous|95|1|0.70|[-0.70, 2.46]|1.000000|
|proposition_straw_manned_present|black|Asian|96|0|-0.35|[-2.43, 1.39]|1.000000|
|proposition_straw_manned_present|black|Indigenous|96|0|0.35|[-0.69, 1.74]|1.000000|
|proposition_straw_manned_present|Asian|Indigenous|96|0|0.69|[0.00, 1.74]|1.000000|
|proposition_unclear_present|white|black|95|1|0.00|[0.00, 0.00]|1.000000|
|proposition_unclear_present|white|Asian|95|1|0.00|[0.00, 0.00]|1.000000|
|proposition_unclear_present|white|Indigenous|95|1|0.00|[0.00, 0.00]|1.000000|
|proposition_unclear_present|black|Asian|96|0|0.00|[0.00, 0.00]|1.000000|
|proposition_unclear_present|black|Indigenous|96|0|0.00|[0.00, 0.00]|1.000000|
|proposition_unclear_present|Asian|Indigenous|96|0|0.00|[0.00, 0.00]|1.000000|
