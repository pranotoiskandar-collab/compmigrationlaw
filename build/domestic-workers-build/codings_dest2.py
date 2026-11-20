# Added 2026-11-11 (v1.1, Pranoto: "yes, add them"). All cells S (secondary sources), to be checked against official texts.
RAW = {
"MA": """cov|1|Dedicated statute with narrower terms than the Labour Code.|Law 19-12 (2016, in force 2018)
con|1|Written contract on a model form, deposited with the labor inspector.|Law 19-12 art. 3
wage|1|Minimum wage set at 60% of the general minimum (SMIG).|Law 19-12 art. 19; Decree 2.17.355
pay|1|Monthly payment.|Law 19-12
hrs|1|48 hours a week, above the Labour Code's 44.|Law 19-12 art. 13
rest|2|At least 24 consecutive hours each week.|Law 19-12 art. 14
leave|2|1.5 days per month of service.|Law 19-12 art. 15
doc|1|General law.|
live|1|Accommodation rules not specific.|
mob|1|Foreign workers need a contract approved by the labor ministry.|
fee||Not determined.|
agen|1|Intermediaries regulated.|Law 19-12 art. 4
insp|1|Labor inspector conciliation on complaint.|Law 19-12 art. 22
disp|1|Inspector conciliation, then courts.|Law 19-12 art. 22
soc|2|Covered by the national social security fund (CNSS) since 2019.|Decree 2.18.686
viol|1|Prohibits forced labor and violence; penalties in the law.|Law 19-12 arts 11, 23
org||Not determined.|""",
"TH": """cov|1|Ministerial Regulation applies selected provisions of the Labour Protection Act to domestic work.|Ministerial Regulation No. 14 (2012)
con|0|No written contract required (MoU workers have contracts under the recruitment scheme).|
wage|0|Minimum wage does not apply.|
pay|1|Wage payment provisions apply.|Ministerial Regulation No. 14
hrs|0|No limit.|
rest|1|One weekly holiday; may be agreed otherwise.|Ministerial Regulation No. 14
leave|1|Six days' paid annual leave after one year.|Ministerial Regulation No. 14
doc|1|Royal Ordinance bars employers from keeping workers' documents.|Royal Ordinance on Management of Foreign Workers 2017
live|0|No rule.|
mob|1|Change of employer allowed in listed cases.|Royal Ordinance 2017
fee|1|Recruitment fees on workers restricted.|Royal Ordinance 2017
agen|1|Licensed recruitment agencies.|Royal Ordinance 2017
insp|1|Complaint-based.|
disp|1|Labor protection officers, then labor courts.|
soc|0|Excluded from the Social Security Act.|Social Security Act 1990
viol|1|Sexual harassment provisions apply.|Ministerial Regulation No. 14
org|1|Migrant workers may join but not form unions.|Labour Relations Act 1975""",
"PK": """cov|2|Provincial statute granting core labor rights (Punjab as reference; Islamabad Act 2022 similar).|Punjab Domestic Workers Act 2019
con|1|Letter of appointment.|Punjab Domestic Workers Act 2019
wage|2|Minimum wage notified for domestic workers.|Punjab Domestic Workers Act 2019
pay|1|Monthly payment.|
hrs|2|8 hours a day.|Punjab Domestic Workers Act 2019
rest|2|One day of weekly rest.|Punjab Domestic Workers Act 2019
leave|1|Casual, sick and festival leave.|Punjab Domestic Workers Act 2019
doc|0|No rule.|
live|1|Decent accommodation for live-in workers.|
mob||Not determined.|
fee||Not determined.|
agen||Not determined.|
insp|1|Inspectors under the Act.|
disp|2|Domestic Workers Dispute Resolution Committees.|Punjab Domestic Workers Act 2019
soc|2|Social security registration.|Punjab Domestic Workers Act 2019
viol|2|Protection from harassment; child domestic work below 15 prohibited.|Punjab Domestic Workers Act 2019
org|2|May form and join unions.|Punjab Domestic Workers Act 2019""",
"BR": """cov|2|Dedicated law extending general labor rights to domestic workers.|Complementary Law 150/2015; Constitutional Amendment 72/2013
con|1|Registration in the work booklet.|LC 150/2015
wage|2|National minimum wage applies.|
pay|2|Monthly payment; deductions for food and housing prohibited.|LC 150/2015 art. 18
hrs|2|8 hours a day, 44 a week, overtime paid.|LC 150/2015 art. 2
rest|2|Weekly paid rest.|LC 150/2015
leave|2|30 days.|LC 150/2015 art. 17
doc|1|General law.|
live|2|Live-in or live-out; housing not deducted.|LC 150/2015 art. 18
mob|2|Residence not tied to one employer (Mercosur and humanitarian visas).|
fee||Not determined.|
agen|1|General rules.|
insp|1|Inspection of homes needs consent or scheduling.|LC 150/2015 art. 44
disp|2|Labor courts.|
soc|2|INSS, FGTS and unemployment insurance (eSocial).|LC 150/2015
viol|1|General law.|
org|2|May form and join unions.|""",
"MX": """cov|2|Federal Labor Law chapter on domestic work, reformed 2019.|Ley Federal del Trabajo arts 331-343-E (reform 2019)
con|2|Written contract required.|LFT art. 331 Ter
wage|2|Minimum wage applies; a professional minimum set by the wage commission.|LFT art. 335
pay|2|Payment rules apply; in-kind pay limited.|LFT
hrs|2|8 hours a day.|LFT art. 333
rest|2|Day and a half of weekly rest.|LFT art. 336
leave|2|Annual leave as for other workers.|LFT
doc|1|General law.|
live|2|Live-in or live-out; decent room.|LFT art. 337
mob|1|Residence permits linked to an offer.|
fee||Not determined.|
agen|1|General rules.|
insp|1|Complaint-based.|
disp|2|Labor courts.|
soc|2|Mandatory social security (IMSS).|LFT art. 337 bis
viol|1|General law.|
org|2|May form and join unions.|""",
"CR": """cov|2|Labor Code chapter on domestic work, reformed 2009.|Law 8726 (2009)
con|1|Written contract not required.|
wage|2|Minimum wage applies.|
pay|2|Payment rules apply.|
hrs|2|8 hours a day, 48 a week.|Law 8726
rest|2|Weekly rest.|Law 8726
leave|2|Two weeks.|Law 8726
doc|1|General law.|
live|2|Live-in or live-out; decent accommodation.|Law 8726
mob|1|Work permits linked to employment.|
fee||Not determined.|
agen|0|No licensing.|
insp|1|Complaint-based.|
disp|2|Labor courts.|
soc|2|Social security (CCSS).|
viol|1|General law.|
org|2|May form and join unions.|""",
"BO": """cov|2|Dedicated statute on salaried household work.|Law 2450 (2003)
con|1|Contract may be oral.|Law 2450
wage|2|National minimum wage applies.|Law 2450
pay|1|Monthly payment.|
hrs|1|8 hours for live-out, 10 for live-in workers.|Law 2450
rest|2|Weekly rest.|Law 2450
leave|2|Annual leave.|Law 2450
doc|1|General law.|
live|1|Accommodation and food for live-in workers.|Law 2450
mob|2|Residence not tied to one employer.|
fee||Not determined.|
agen|0|No licensing.|
insp|1|Complaint-based.|
disp|2|Labor courts.|
soc|1|Health insurance; pensions partly.|
viol|1|General law.|
org|2|May form and join unions.|""",
"PE": """cov|2|Dedicated law aligned with C189.|Law 31047 (2020)
con|2|Written contract registered with the labor ministry.|Law 31047 art. 5
wage|2|Minimum wage applies.|Law 31047
pay|2|Payment rules; in-kind pay excluded.|Law 31047
hrs|2|8 hours a day, 48 a week.|Law 31047
rest|2|24 hours a week.|Law 31047
leave|2|30 days.|Law 31047
doc|1|General law.|
live|2|Live-in or live-out; decent accommodation.|Law 31047
mob|1|Residence permits linked to employment.|
fee||Not determined.|
agen|1|Agencies regulated.|Law 31047
insp|1|Inspection with safeguards for the home.|Law 31047
disp|2|Labor courts.|
soc|2|Social security.|Law 31047
viol|2|Specific protection from harassment and violence.|Law 31047
org|2|May form and join unions.|""",
"CL": """cov|2|Labor Code chapter on domestic work, reformed 2014.|Law 20.786 (2014)
con|2|Written contract within 15 days, registered with the labor directorate.|Law 20.786
wage|2|Minimum wage applies.|
pay|2|In-kind pay may not be deducted.|Law 20.786
hrs|2|45 hours for live-out workers; 12 hours' rest for live-in workers.|Law 20.786
rest|2|Sunday rest, Saturdays for live-in workers.|Law 20.786
leave|2|Annual leave as for other workers.|
doc|1|General law.|
live|2|Live-in or live-out; decent accommodation.|Law 20.786
mob|1|Residence permits linked to employment.|
fee||Not determined.|
agen|1|General rules.|
insp|1|Registration-based checks.|
disp|2|Labor courts.|
soc|2|Social security.|
viol|1|General law.|
org|2|May form and join unions.|""",
"PY": """cov|2|Dedicated law on domestic work.|Law 5407 (2015)
con|1|Contract may be oral.|Law 5407
wage|2|Minimum wage applies in full since 2019.|Law 6338 (2019)
pay|2|Payment rules apply.|Law 5407
hrs|2|8 hours a day.|Law 5407
rest|2|Weekly rest.|Law 5407
leave|2|Annual leave.|Law 5407
doc|1|General law.|
live|2|Live-in or live-out.|Law 5407
mob|2|Residence not tied to one employer (Mercosur).|
fee||Not determined.|
agen|0|No licensing.|
insp|1|Complaint-based.|
disp|2|Labor courts.|
soc|2|Social security (IPS).|Law 5407
viol|1|General law.|
org|2|May form and join unions.|""",
"UY": """cov|2|Dedicated law granting general labor rights.|Law 18.065 (2006)
con|1|Registration with social security.|
wage|2|Minimum set through the wage councils.|Law 18.065
pay|2|Payment rules apply.|
hrs|2|8 hours a day, 44 a week.|Law 18.065 art. 1
rest|2|36 hours' weekly rest.|Law 18.065 art. 5
leave|2|Annual leave.|
doc|1|General law.|
live|2|9 hours' night rest for live-in workers; live-out permitted.|Law 18.065 art. 4
mob|2|Residence not tied to one employer (Mercosur).|
fee||Not determined.|
agen|1|General rules.|
insp|2|Home inspection with a court order.|Law 18.065 art. 13
disp|2|Labor courts.|
soc|2|Social security and unemployment insurance.|Law 18.065
viol|1|General law.|
org|2|Domestic workers' union bargains in the wage councils.|""",
"NA": """cov|2|Labour Act covers domestic workers; sectoral wage order.|Labour Act 2007; Wage Order 2015
con|1|Written particulars of employment.|Labour Act 2007
wage|1|Sectoral minimum wage for domestic workers.|Wage Order 2015
pay|2|Payment rules apply.|Labour Act 2007
hrs|2|45 hours a week.|Labour Act 2007
rest|2|Weekly rest.|Labour Act 2007
leave|2|Annual leave.|Labour Act 2007
doc|1|General law.|
live|1|Accommodation for live-in workers.|
mob|1|Work visas tied to the employer.|
fee||Not determined.|
agen|1|Private employment agencies regulated.|Employment Services Act 2011
insp|1|Complaint-based.|
disp|2|Labour Commissioner.|
soc|2|Social Security Commission.|
viol|1|General law.|
org|2|May form and join unions.|""",
"ZM": """cov|2|Employment law with a sectoral order for domestic workers.|Employment Code Act 2019; Domestic Workers Order 2011
con|1|Written contract for longer engagements.|Employment Code Act 2019
wage|1|Sectoral minimum wage for domestic workers.|Domestic Workers Order 2011
pay|2|Payment rules apply.|
hrs|2|Hours limits in the order.|Domestic Workers Order 2011
rest|2|Weekly rest.|Domestic Workers Order 2011
leave|2|Annual leave.|Domestic Workers Order 2011
doc|1|General law.|
live|1|Accommodation rules in the order.|
mob|1|Work permits tied to the employer.|
fee||Not determined.|
agen|1|Private employment agencies regulated.|
insp|1|Complaint-based.|
disp|2|Labour office and Industrial Relations Court.|
soc|1|NAPSA pension registration; limited coverage.|
viol|1|General law.|
org|2|May form and join unions.|""",
"TZ": """cov|2|Employment law covers domestic workers; sectoral wage order.|Employment and Labour Relations Act 2004
con|1|Written particulars of employment.|ELRA 2004 s. 15
wage|1|Sectoral minimum wage for domestic workers.|Wage Order (domestic workers)
pay|2|Payment rules apply.|ELRA 2004
hrs|2|45 hours a week.|ELRA 2004 s. 19
rest|2|24 hours a week.|ELRA 2004 s. 24
leave|2|28 days.|ELRA 2004 s. 31
doc|1|General law.|
live|1|Accommodation for live-in workers.|
mob|1|Work permits tied to the employer.|
fee||Not determined.|
agen|1|Private employment agencies regulated.|
insp|1|Complaint-based.|
disp|2|Commission for Mediation and Arbitration.|
soc|1|Social security registration; limited coverage.|
viol|1|General law.|
org|2|May form and join unions.|""",
}
