# Destination codings. One line per cell: key|value|note|source.  value: 2,1,0 or "" (not yet determined).
# AE is coded from the official English translation of Federal Decree-Law No. 9 of 2022 (evidence P);
# every other cell is secondary (S) until checked against the official text.
RAW = {
"AE": """cov|1|Dedicated decree-law; the general labor law (FDL 33/2021) excludes domestic workers. Scope limited to occupations listed in the Executive Regulations.|FDL 9/2022 art. 3; FDL 33/2021 art. 3
con|2|Employment Agreement on the Ministry form, copy delivered to the worker; contracts and forms in Arabic plus a language the worker understands.|FDL 9/2022 arts 7, 28(5)
wage|0|No statutory minimum wage. Art. 28(3) sets a minimum income for the employer, not a wage floor.|FDL 9/2022 art. 28(3)
pay|2|Monthly wage in UAE dirhams within 10 days of the due date, proved by receipt; deductions capped at one quarter. Payment through the Wage Protection System is required for 5 domestic occupations and voluntary for the other 14.|FDL 9/2022 arts 15, 16; Ministerial Resolution 675/2022 art. 2
hrs|1|Daily rest of at least 12 hours, 8 of them consecutive (so at most 12 hours of work a day); no weekly limit and no overtime rule.|FDL 9/2022 art. 9(2); ILO FAIRWAY factsheet (May 2024)
rest|1|Paid weekly rest day; the worker may be required to work it for another rest day or a day's wage, but not on more than two consecutive rest days in two weeks unless agreed.|FDL 9/2022 art. 9(1); Cabinet Resolution 106/2022 art. 8
leave|2|At least 30 days' paid annual leave; return ticket every two years.|FDL 9/2022 art. 10
doc|2|Employer must ensure the worker's right to keep their own identification documents; withholding them carries a fine of AED 500.|FDL 9/2022 art. 11(11); Cabinet Resolution 106/2022 Schedule 2
live|1|Employer must provide suitable accommodation; no rule on living out.|FDL 9/2022 art. 11(2)
mob|1|Transfer during the contract needs the employer's written consent and Ministry approval; without consent only after a judicial decision that the employer breached its obligations, or immediately in cases of assault (reported to the authorities). No exit permit is required.|FDL 9/2022 arts 20-21; Ministerial Resolution 674/2022 art. 2; Cabinet Resolution 106/2022
fee|2|Agencies may not demand or accept any commission or expenses from the worker; employers may not take any amount from the worker.|FDL 9/2022 arts 5(2), 11(13)
agen|2|Licensing by the Ministry; agency bears return costs and is the employer under temporary employment.|FDL 9/2022 arts 4, 5(9), 14
insp|2|Inspectors may enter the employer's home with the owner's or the Public Prosecution's permission, on a complaint or reasonable evidence.|FDL 9/2022 art. 24
disp|2|Ministry settlement within two weeks; the Ministry decides claims up to AED 50,000 with review by the courts (as amended in 2023); worker lawsuits are fee-exempt and urgent; three-month limit after the end of employment.|FDL 9/2022 arts 23, 26 (as amended by FDL 21/2023)
soc|1|Employer bears medical care or health insurance and work-injury compensation; 30 days' sick leave (15 full pay, 15 half pay). No maternity leave, unemployment insurance or pension. End-of-service gratuity: art. 22 leaves it to the Cabinet and no resolution has been issued (checked 12 Nov. 2026); the often-cited 14 days a year came from the repealed Federal Law 10/2017.|FDL 9/2022 arts 10(6), 11(5), (9), 22; Cabinet Resolution 106/2022|P
viol|2|Sexual harassment, forced labor and discrimination prohibited in recruitment; employer must treat the worker with dignity and protect bodily safety.|FDL 9/2022 arts 4(4), 5(6), 11(6)
org|0|Not addressed in the decree-law; UAE labor law does not provide for trade unions.|FDL 9/2022 (no provision); ILO FAIRWAY factsheet (May 2024)""",
"SA": """cov|1|Labour Law art. 7 excludes domestic workers; they are governed by the Domestic Workers Regulation (MD 40676/1445, published October 2023, in force 2024), which replaces MD 310/1434.|Labour Law (M/51, 2005) art. 7; Domestic Workers Regulation, MD 40676/1445|P
con|1|Contract on the ministry's mandatory templates; Arabic text prevails, with a translation into the worker's language; one year by default. The contract is valid even if not in writing, and no copy to the worker is required; Musaned registration is required by ministry procedure.|Domestic Workers Regulation, MD 40676/1445 arts 7-8|P
wage|0|No minimum wage.|Domestic Workers Regulation, MD 40676/1445|P
pay|2|Monthly payment by ministry-approved methods, deductions capped at 25 per cent; digital-wallet payment compulsory for all domestic workers, phased in July 2024 to January 2026.|Domestic Workers Regulation, MD 40676/1445 arts 17-20; HRSD|P
hrs|1|At most 10 hours' work a day, at least 8 consecutive hours' rest and a break of at least 30 minutes after five hours; longer than the 8-hour norm under the Labour Law.|Domestic Workers Regulation, MD 40676/1445 art. 10|P
rest|2|One paid rest day a week.|Domestic Workers Regulation, MD 40676/1445 art. 11|P
leave|1|30 days' paid leave after every two years if the contract is renewed (the Labour Law gives 21 days a year).|Domestic Workers Regulation, MD 40676/1445 art. 12|P
doc|2|The employer may not keep the worker's passport or personal documents.|Domestic Workers Regulation, MD 40676/1445 art. 15(2)|P
live|1|Suitable housing and food (or a cash allowance), and the right to contact family, embassy and authorities; no rule on privacy.|Domestic Workers Regulation, MD 40676/1445 art. 15(7)-(8)|P
mob|1|Transfer without the employer's consent in 12 listed cases (e.g. three unpaid wages, no residence permit, being hired out, dangerous work, abuse, employer's delay in a complaint); final exit at the end of the contract. No general right to change employer; the 2021 labour reforms exclude domestic workers.|Domestic Workers Regulation, MD 40676/1445 art. 27; MD 212875/1443; HRSD rules on the contractual relationship (2024) art. 5(3)|P
fee|2|The employer bears recruitment costs and fees; recruitment companies may not take any sum from the worker or receive payments outside the Musaned platform.|Domestic Workers Regulation, MD 40676/1445 art. 15(1); Recruitment Rules, MD 119698 (2025) arts 42, 50|P
agen|2|Recruitment companies are licensed with bank guarantees (SAR 2-10 million by category) that the ministry may draw on for unpaid worker dues or return costs; the licensee is liable for the worker it placed and must house absent workers; replacement or refund during the 90-day probation.|Recruitment Rules, MD 119698 (2025) arts 8, 13, 46, 49, 53, 59; Domestic Workers Regulation, MD 40676/1445 art. 9|P
insp|0|The regulation gives no power to inspect households; enforcement is complaint-based.|Domestic Workers Regulation, MD 40676/1445|P
disp|1|Complaints to the ministry, which seeks an amicable settlement; claims lapse after 12 months.|Domestic Workers Regulation, MD 40676/1445 art. 32|P
soc|1|30 days' sick leave a year (15 at full pay, 15 at half pay); end-of-service award of one month's wage per four years; health insurance under the 2024 framework; no maternity leave.|Domestic Workers Regulation, MD 40676/1445 arts 13, 22|P
viol|2|Violence, harassment, forced labour and trafficking prohibited; employer fines up to SAR 20,000 and/or a recruitment ban.|Domestic Workers Regulation, MD 40676/1445 arts 15(3)-(6), 29|P
org|0|No provision in the regulation; migrant workers may not join workers' committees.|Domestic Workers Regulation, MD 40676/1445; CoM Decree 12/1422|P""",
"KW": """cov|1|Private-sector labor law excludes domestic workers; dedicated Law 68/2015 with Ministerial Decisions 2194/2016 and 22/2022.|Law 6/2010 art. 5; Law 68/2015; MD 2194/2016; MD 22/2022; ILO FAIRWAY factsheet (Dec. 2023)
con|1|Contract on the form prescribed by the Domestic Workers Department, in English and Arabic (not necessarily a language the worker understands); renewable annually.|Law 68/2015; ILO factsheet
wage|2|Minimum wage of KWD 75 a month, the same figure as for the private sector.|MD 22/2022 art. 27; MD 14/2017
pay|2|Monthly, within seven days of the due date, against a receipt; KWD 10 penalty for each month of delay.|Law 68/2015; ILO factsheet
hrs|1|Up to 12 hours a day including breaks; the standard contract adds an hour's rest after five hours and 8 consecutive hours of night rest; up to two extra hours paid at half a day's wage.|Law 68/2015 art. 22(2); Standard Contract (2020) art. 7(3); MD 22/2022 art. 30
rest|1|One day per week.|Law 68/2015 art. 22(3)
leave|2|30 days' paid annual leave after 11 months.|MD 22/2022 art. 28
doc|1|Confiscation prohibited, but the employer may keep the passport and ID with the worker's consent.|MD 2194/2016 art. 8(8); MD 22/2022 art. 23
live|1|Decent food and housing; the worker may own and use a mobile phone and contact family outside working hours.|MD 22/2022 art. 23
mob|1|Transfer with the employer's permission; without it, only in listed cases (employer's death or departure, divorce, ineligibility or imprisonment, proven sexual misconduct). No exit permit is required.|ILO factsheet; MD 22/2022
fee|2|Neither the employer nor the recruitment agency may recover recruitment costs from the worker; agencies may not charge "advance wages".|MD 22/2022 art. 21; ILO factsheet
agen|2|Licensed offices; liability during the probation period.|Law 68/2015 arts 3-13
insp|1|Complaint-based.|Law 68/2015
disp|2|Domestic Workers Department investigates and decides within two weeks; unresolved cases go to the Civil Court (Labour Circuit) free of court fees.|MD 22/2022 art. 34; CoM Decision 614/2018; ILO factsheet
soc|1|Mandatory employer-paid health insurance; injury treatment and compensation in the contract; end-of-service pay of one month per year. No sick or maternity leave in the law.|Law 68/2015 art. 23; MD 2194/2016 art. 13; Law 1/1999 art. 2
viol|1|Harmful, dangerous or degrading work prohibited; government shelter for women workers (since 2014).|MD 22/2022; MD 2194/2016 art. 27
org|0|No provision enabling domestic workers to join a trade union.|Labour Law art. 99; ILO factsheet""",
"QA": """cov|1|Labour Law art. 3 excludes domestic workers; dedicated Law 15/2017 and the Standard Unified Contract.|Law 14/2004 art. 3; Law 15/2017; ILO FAIRWAY factsheet (Dec. 2023)
con|2|Written contract on the Standard Unified Contract, authenticated by the ministry, bilingual (Arabic and another language).|Law 15/2017 art. 5; ILO FAIRWAY factsheet (Dec. 2023)
wage|2|National minimum wage (QAR 1,000 a month) applies to domestic workers, plus QAR 500 housing and QAR 300 food if not provided.|Law 17/2020; ILO FAIRWAY factsheet (Dec. 2023)
pay|2|Paid at the end of the month and no later than the third day of the next, by bank account or in cash against a signed receipt; recruitment costs may not be deducted.|Law 15/2017 art. 8; ILO FAIRWAY factsheet (Dec. 2023)
hrs|1|Law sets a 10-hour daily cap excluding breaks; the standard contract sets 8 normal hours plus up to 2 hours' overtime at 125 per cent.|Law 15/2017 art. 12; Standard Unified Contract art. 4; ILO FAIRWAY factsheet (Dec. 2023)
rest|2|One rest day a week.|Law 15/2017 art. 12
leave|2|Three weeks' paid annual leave a year, and a return air ticket home every two years.|Law 15/2017 art. 14; ILO FAIRWAY factsheet (Dec. 2023)
doc|1|Confiscating passports is an offence (fine up to QAR 25,000), but the employer may keep the passport with the worker's written consent.|Law 21/2015 arts 8, 33; ILO FAIRWAY factsheet (Dec. 2023)
live|1|Suitable accommodation and food; no specific occupational safety or accommodation standard for domestic workers.|Law 15/2017 art. 9; ILO FAIRWAY factsheet (Dec. 2023)
mob|2|Change of employer at any time without the employer's permission, with one or two months' notice through the ministry system (compensation capped at two months' wage during probation); no exit permit, 72 hours' notice before leaving the country.|Law 21/2015 and Executive Regulations arts 7, 65; ILO FAIRWAY factsheet (Dec. 2023)
fee|2|The standard contract places recruitment fees on the agency or employer and bars deductions from the worker.|Law 15/2017; Standard Unified Contract; ILO FAIRWAY factsheet (Dec. 2023)
agen|2|Licensed offices; liability for return in the probation period.|Law 15/2017 arts 3-4
insp|1|Complaint-based, including the online Unified Platform for Complaints and Whistleblowers.|ILO FAIRWAY factsheet (Dec. 2023)
disp|2|Ministry conciliation, then the Labour Dispute Settlement Committee (decision within three weeks, appeal to the Appellate Court, no court fees); unpaid awards via the Workers' Support and Insurance Fund.|Law 13/2017; Cabinet Decision 6/2018; Law 17/2018; ILO FAIRWAY factsheet (Dec. 2023)
soc|1|Employer-paid medical care for sickness or injury; up to two weeks' paid sick leave after three months; end-of-service gratuity of three weeks' pay a year; maternity not specified.|Law 15/2017 art. 15; Standard Unified Contract; ILO FAIRWAY factsheet (Dec. 2023)
viol|1|Two government shelters for trafficking victims; complaints to the National Committee to Combat Human Trafficking.|ILO FAIRWAY factsheet (Dec. 2023)
org|0|Worker committees are open to Qatari workers only; joint committees exist at enterprises with 30 or more workers, which does not fit household employment.|Law 14/2004 art. 116, ch. 13; ILO FAIRWAY factsheet (Dec. 2023)""",
"BH": """cov|1|Domestic workers benefit only from Labour Law articles listed in art. 2 (contract, wages, leave, gratuity, court-fee exemption, non-discrimination since 2018).|Law 36/2012 art. 2; ILO FAIRWAY factsheet (Dec. 2023)
con|1|Standard tripartite contract (agency, worker, employer) plus a contract between worker and employer; BHD 200-500 penalty for non-compliance; language rule not stated.|Law 36/2012; Decision 4/2014; ILO FAIRWAY factsheet (Dec. 2023)
wage|0|No minimum wage (the minimum wage covers only Bahraini public-sector workers).|ILO FAIRWAY factsheet (Dec. 2023)
pay|1|Monthly payment; domestic workers are outside the Wages Protection Scheme unless the employer opts in.|Law 36/2012 art. 2; Decision 68/2019; ILO FAIRWAY factsheet (Dec. 2023)
hrs|0|Working hours not specified.|Law 36/2012 art. 2; ILO FAIRWAY factsheet (Dec. 2023)
rest|0|Weekly rest not specified.|Law 36/2012 art. 2; ILO FAIRWAY factsheet (Dec. 2023)
leave|2|30 days' annual leave.|Law 36/2012 arts 2, 58; ILO FAIRWAY factsheet (Dec. 2023)
doc|2|Employers may not confiscate passports.|Penal Code art. 395; ILO FAIRWAY factsheet (Dec. 2023)
live|1|The standard contract requires decent housing, privacy, food, clothing, safety, medical care and regular contact with family.|LMRA standard contract; ILO FAIRWAY factsheet (Dec. 2023)
mob|1|Change of employer at any time with permission; without it, only with LMRA approval. Domestic workers have one week (others 30 days) to contest an absconding report.|Decision 4/2014; ILO FAIRWAY factsheet (Dec. 2023)
fee|2|No person may take money or any benefit from a worker for a work permit, employment or keeping the job; prison of 3 months to 1 year and/or BHD 1,000-2,000, aggravated for domestic-worker permits and multiplied by the number of workers.|Law 19/2006 arts 23(C), 36(A)|P
agen|1|LMRA licence with Bahraini ownership, approved contract templates and a BHD 10,000 guarantee (which compensates employers only); offices placing women domestic workers must provide temporary housing supervised by a woman.|LMRA Board Resolution 1/2014 (as amended) arts 2, 6, 9|P
insp|0|No household inspection.|
disp|2|Ministry settlement or direct LMRA filing with translation and document help; no filing fee; hearing within two months.|Law 36/2012 arts 2, 119, 135; ILO FAIRWAY factsheet (Dec. 2023)
soc|1|Compulsory private health insurance includes domestic workers; end-of-service gratuity applies; sick leave, injury and maternity not specified; optional employer insurance.|Law 23/2018 art. 26; Law 36/2012 art. 2; ILO FAIRWAY factsheet (Dec. 2023)
viol|1|LMRA Expatriate Protection Unit shelter for trafficking victims; hotline 995; general criminal law.|ILO FAIRWAY factsheet (Dec. 2023)
org|2|All workers, including domestic workers, may join and in principle form trade unions.|Law 33/2002 art. 10; ILO FAIRWAY factsheet (Dec. 2023)""",
"OM": """cov|1|Domestic workers are outside the Labour Law but covered by a dedicated regulation with fines (OMR 50-500 per violation, multiplied by the number of workers); it repeals MR 189/2004.|MD 574/2025 (Official Gazette 1617, 12 Oct. 2025) Reg. art. 39|P
con|1|Written contract in Arabic, registered online with the ministry.|MD 574/2025 Reg. art. 19|P
wage|0|The minimum wage does not apply to migrant workers.|ILO FAIRWAY factsheet (Dec. 2023)|S
pay|2|Paid in Omani rials within seven days of the due date, proved by a signed register or a local bank account; the ministry may set a payment system; deductions capped at 25 per cent.|MD 574/2025 Reg. arts 27-29|P
hrs|1|Up to 12 hours a day with at least 8 hours' rest; up to 2 hours' paid overtime by written agreement. Longer than the 8-hour norm for other workers.|MD 574/2025 Reg. art. 22|P
rest|2|At least one paid rest day a week; work on that day only with written consent and extra pay or a substitute day.|MD 574/2025 Reg. art. 23|P
leave|2|At least 21 days' paid annual leave; untaken leave paid out at the end of service.|MD 574/2025 Reg. art. 25|P
doc|1|The employer may not keep the passport or documents except with the worker's written consent.|MD 574/2025 Reg. art. 5|P
live|2|Food and suitable housing: a ventilated, lit and air-conditioned room with a bed, wardrobe and proper toilet; free transport for workers living out.|MD 574/2025 Reg. arts 13-15|P
mob|1|No unilateral right to change employer: transfer by agreement only. The worker may leave without notice, keeping all rights, if wages are unpaid for over two months or in cases of fraud, assault or serious danger.|MD 574/2025 Reg. arts 32, 36|P
fee|2|The employer may not take any money from the worker for recruitment, employment or transfer; agency fees are barred by the 2011 agency rules.|MD 574/2025 Reg. art. 7; MD 1/2011|P
agen|1|Licensed recruitment offices; the office may notify the ministry on the worker's behalf.|MD 574/2025 Reg. art. 38; MD 1/2011|P
insp|1|Ministry inspectors may interview the worker and request documents; a home visit needs the Public Prosecution's permission.|MD 574/2025 Reg. art. 12|P
disp|2|Labour Law dispute procedure applies; the worker pays no court fees at any stage.|MD 574/2025 Reg. art. 37; Royal Decree 53/2023 art. 9|P
soc|1|Up to 30 days' paid sick leave a year; health insurance; end-of-service pay of half a month's wage a year after two years' service (counted from the regulation's entry into force); maternity not provided.|MD 574/2025 Reg. arts 16, 24, 31|P
viol|1|Forced labour and violence banned; degrading advertising of workers banned; the worker may leave after assault.|MD 574/2025 Reg. arts 4, 10, 36|P
org|0|The regulation has no provision on association; Labour Law union rights do not extend to domestic workers.|MD 574/2025 Reg.; Royal Decree 53/2023 arts 108-111|P""",
"JO": """cov|2|Domestic workers brought under the Labour Law in 2008, with a dedicated regulation.|Labour Law 8/1996 art. 3 as amended 2008; Regulation 90/2009
con|2|Unified tripartite contract in Arabic and the worker's language.|Regulation 90/2009 art. 3
wage|1|Excluded from the national minimum wage; minimums set by bilateral arrangement per nationality.|
pay|1|Monthly payment, by bank transfer where possible.|Regulation 90/2009 art. 4
hrs|1|Maximum 10 hours a day.|Regulation 90/2009 art. 5
rest|2|One weekly rest day.|Regulation 90/2009 art. 5
leave|1|14 days' paid annual leave.|Regulation 90/2009 art. 6
doc|2|Withholding another person's passport is an offence.|Passports Law art. 23
live|1|Suitable accommodation and food.|Regulation 90/2009 art. 4
mob|1|Transfer in listed cases.|
fee|2|Recruitment offices may not charge workers.|Regulation on recruitment offices (2015)
agen|2|Licensed offices; liability in the first months.|
insp|1|Complaint-based.|
disp|1|Labour Directorate settlement, then courts.|
soc|1|Medical care by the employer.|
viol|1|General criminal law; anti-trafficking law.|Law 9/2009
org||Not determined.|""",
"LB": """cov|0|Labour Code art. 7 excludes domestic workers; terms set by the Unified Standard Contract and the sponsorship system. A 2020 revised contract was suspended by the Shura Council.|Labour Code 1946 art. 7; Unified Standard Contract 2009
con|1|Standard contract required for the work permit.|Unified Standard Contract 2009
wage|0|No minimum wage.|
pay|1|Monthly payment with receipt.|Unified Standard Contract 2009
hrs|1|8 hours' continuous night rest.|Unified Standard Contract 2009
rest|1|24 hours' weekly rest, usually spent at the employer's home.|Unified Standard Contract 2009
leave|1|Six days' paid annual leave.|Unified Standard Contract 2009
doc|0|No binding rule; the 2020 contract provision is suspended.|
live|1|Accommodation and food by the employer.|Unified Standard Contract 2009
mob|0|Change needs the employer's release.|
fee|1|Recruitment office rules; fees not prohibited for workers.|
agen|1|Licensed offices.|Decree 1/2009 (to verify)
insp|0|No household inspection.|
disp|1|Civil courts and the Ministry of Labour complaints office.|
soc|1|Employer-purchased insurance.|
viol|1|General criminal law; anti-trafficking law.|Law 164/2011
org|0|No right recognized for domestic workers.|""",
"IL": """cov|2|Labor laws apply to migrant caregivers, except the Hours of Work and Rest Law for live-in caregivers.|Foreign Workers Law 1991; HCJ 1678/07 Gloten (2009)
con|2|Written contract in a language the worker understands.|Foreign Workers Law 1991 s. 1G
wage|2|National minimum wage applies.|Minimum Wage Law 1987
pay|2|Wage Protection Law applies; deductions for housing capped.|Wage Protection Law 1958
hrs|0|Hours of Work and Rest Law does not apply to live-in caregivers.|HCJ 1678/07 Gloten
rest|1|Weekly rest by extended agreement; not enforceable under the Rest Law.|
leave|2|Annual Leave Law applies.|Annual Leave Law 1951
doc|2|Withholding a passport is an offence.|Foreign Workers Law; Penal Law s. 376A
live|1|Employer must provide suitable housing.|Foreign Workers Law s. 1D
mob|1|Change within the caregiving sector with limits.|
fee|1|Recruitment fees capped by regulation; bilateral agreements reduce them further.|
agen|2|Licensed agencies with supervision duties.|Employment Service Law 1959
insp|1|Complaint-based.|
disp|2|Labour courts.|
soc|1|Health insurance by the employer; partial National Insurance.|
viol|1|General law; anti-trafficking law.|
org|2|May form and join unions.|""",
"HK": """cov|2|Employment Ordinance covers foreign domestic helpers; mandatory Standard Employment Contract.|Employment Ordinance (Cap. 57); ID 407
con|2|Standard Employment Contract in English and Chinese, signed before the visa is granted.|ID 407
wage|1|Statutory Minimum Wage excludes live-in domestic workers; a separate Minimum Allowable Wage is set by policy.|Minimum Wage Ordinance (Cap. 608) s. 7
pay|2|Wages within 7 days of the due date; deductions restricted.|Cap. 57 ss. 23-32
hrs|0|No limit on working hours.|
rest|2|One rest day of at least 24 continuous hours each week.|Cap. 57 s. 17
leave|2|Paid annual leave of 7-14 days as for other employees.|Cap. 57 s. 41AA
doc|1|Code of Practice bars agencies from keeping documents; general offence of unlawfully withholding documents.|Code of Practice for Employment Agencies
live|1|Mandatory live-in rule; contract requires suitable accommodation with reasonable privacy.|ID 407 cl. 3
mob|1|May change employer on termination, but must leave within two weeks or find a new employer.|Immigration policy (two-week rule)
fee|1|Agencies may charge at most 10% of the first month's wage.|Employment Agency Regulations (Cap. 57A)
agen|1|Licensed agencies; 2018 amendments raised penalties.|Cap. 57 Part XII
insp|1|Complaint-based.|
disp|2|Labour Tribunal and Minor Employment Claims Adjudication Board.|
soc|1|Employees' Compensation and maternity protection apply; Mandatory Provident Fund excludes helpers.|
viol|1|General criminal law.|
org|2|May form and join trade unions.|Trade Unions Ordinance (Cap. 332)""",
"SG": """cov|1|Employment Act excludes domestic workers; Employment of Foreign Manpower Act and work permit conditions apply.|Employment Act s. 2; EFMA (Cap. 91A)
con|1|Work permit conditions; standard contracts used by agencies.|EFMA Regulations Fourth Schedule
wage|0|No minimum wage.|
pay|1|Monthly salary within 7 days, with records.|EFMA Regulations Fourth Schedule
hrs|1|At least 8 continuous hours of rest daily.|EFMA Regulations Fourth Schedule
rest|1|Weekly rest day, which may be compensated; at least one rest day a month that cannot be compensated (2023).|EFMA Regulations Fourth Schedule
leave|0|No statutory annual leave.|
doc|1|Employers must not keep the worker's work permit card; passport rule in guidance.|
live|1|Acceptable accommodation with ventilation and privacy; living in required.|EFMA Regulations Fourth Schedule
mob|1|Transfer with the employer's consent or at the end of the contract.|
fee|1|Agency fees capped at one month's salary per year of contract, up to two months.|Employment Agencies Act
agen|1|Licensed agencies with a demerit system.|Employment Agencies Act
insp|1|Ministry interviews and home visits for first-time workers.|
disp|1|Ministry mediation of salary claims.|
soc|1|Compulsory medical and personal accident insurance.|EFMA Regulations Fourth Schedule
viol|2|Enhanced penalties for offences against domestic workers by employers.|Penal Code s. 73
org||Not determined.|""",
"MY": """cov|1|Employment Act covers domestic employees only in part (First Schedule).|Employment Act 1955 First Schedule (as amended 2022)
con|1|Written contract for the work permit.|
wage|0|Minimum Wages Order excludes domestic employees.|Minimum Wages Order
pay|1|Wage payment rules partly apply.|Employment Act 1955
hrs|0|Hours provisions do not apply.|Employment Act 1955 First Schedule
rest|0|Rest-day provisions do not apply.|Employment Act 1955 First Schedule
leave|0|Annual leave provisions do not apply.|Employment Act 1955 First Schedule
doc|2|Unlawful possession of another person's passport is an offence.|Passports Act 1966 s. 12(1)(f)
live|0|No rule.|
mob|0|Change needs the employer's consent.|
fee|1|Fees regulated under the Private Employment Agencies Act.|Private Employment Agencies Act 1981 (am. 2017)
agen|1|Licensed agencies.|Private Employment Agencies Act 1981
insp|0|No household inspection.|
disp|1|Labour Court for wage claims.|Employment Act 1955 s. 69
soc|1|Employment injury scheme covers foreign domestic workers since 2021.|Employees' Social Security Act 1969
viol|1|General criminal law; anti-trafficking law.|
org||Not determined.|""",
"TW": """cov|0|Labor Standards Act does not apply to household workers; the Employment Service Act governs foreign household workers. A Domestic Workers Protection bill is pending.|Employment Service Act 1992
con|1|Contract required for the permit; standard contract by the ministry.|Employment Service Act
wage|1|Excluded from the statutory minimum; a minimum set by policy for household caregivers.|
pay|1|Monthly payment.|
hrs|0|No limit.|
rest|1|Weekly rest day by contract, which may be worked for pay.|
leave|1|Annual leave by contract.|
doc|2|Employers and agencies may not keep the worker's passport or residence permit.|Employment Service Act art. 54
live|1|Accommodation in the employer's home.|
mob|1|Change allowed with agreement or in listed cases.|Employment Service Act art. 59
fee|1|Service fees capped by the ministry.|
agen|1|Licensed agencies with ratings.|
insp|1|Complaint-based.|
disp|1|Labor bureau mediation.|
soc|1|National Health Insurance compulsory.|
viol|1|General law; sexual harassment law.|
org||Not determined.|""",
"IT": """cov|2|Labor law with a special regime for domestic work and a binding national collective agreement.|Law 339/1958; CCNL Lavoro Domestico
con|2|Written letter of employment; a translation is customary.|Legislative Decree 104/2022
wage|2|Minimum pay set by the national collective agreement.|CCNL Lavoro Domestico
pay|2|Monthly pay slip and payment; limits on in-kind pay.|CCNL Lavoro Domestico
hrs|1|54 hours a week for live-in workers, 40 for others.|CCNL Lavoro Domestico
rest|2|36 hours' weekly rest, 24 of them on Sunday.|CCNL Lavoro Domestico
leave|2|26 working days.|CCNL Lavoro Domestico
doc|1|General criminal law.|
live|2|Live-out or live-in; live-in accommodation must be suitable and private.|CCNL Lavoro Domestico
mob|2|Work permit not tied to one employer.|Legislative Decree 286/1998
fee|2|Agencies may not charge workers.|Legislative Decree 276/2003 art. 11
agen|2|Authorized agencies.|Legislative Decree 276/2003
insp|1|Inspection of homes limited by the constitutional protection of the home.|Constitution art. 14
disp|2|Labor courts.|
soc|2|INPS social insurance, including maternity.|
viol|2|C190 ratified; criminal law on labor exploitation.|Criminal Code art. 603-bis
org|2|May form and join unions.|""",
"ES": """cov|2|Special employment relationship under the Workers' Statute; 2022 reform added unemployment benefit and ended dismissal without cause.|Royal Decree 1620/2011; Royal Decree-Law 16/2022
con|2|Written contract for work longer than four weeks.|RD 1620/2011 art. 5
wage|2|National minimum wage applies.|RD 1620/2011 art. 8
pay|2|Monthly pay with a pay slip; in-kind pay limited to 30%.|RD 1620/2011 art. 8
hrs|1|40 hours plus paid presence time of up to 20 hours.|RD 1620/2011 art. 9
rest|2|36 consecutive hours a week.|RD 1620/2011 art. 9
leave|2|30 calendar days.|RD 1620/2011 art. 9
doc|1|General criminal law.|
live|2|Live-in or live-out; dignity and privacy of accommodation.|RD 1620/2011 art. 9
mob|1|First authorization limited to one sector and region for one year.|Organic Law 4/2000
fee|2|Agencies may not charge workers.|Royal Legislative Decree 3/2015
agen|2|Authorized agencies.|
insp|1|Labor inspection must respect the inviolability of the home.|RD 1620/2011 art. 12
disp|2|Labor courts.|
soc|2|Included in the general social security system, including maternity and unemployment.|RDL 16/2022
viol|2|C190 ratified.|
org|2|May form and join unions.|""",
"GB": """cov|2|Employment law applies, with exemptions from working-time limits and a family-worker exemption from the minimum wage.|Employment Rights Act 1996; Working Time Regulations 1998 reg. 19
con|2|Written statement of terms from day one; the Overseas Domestic Worker visa requires written terms.|Employment Rights Act 1996 s. 1; Immigration Rules Appendix ODW
wage|1|Minimum wage applies, except under the family-worker exemption.|National Minimum Wage Regulations 2015 reg. 57
pay|2|Itemized pay statements; deductions regulated.|Employment Rights Act 1996 Part II
hrs|1|Daily rest applies; weekly limit and night-work rules do not.|Working Time Regulations 1998 reg. 19
rest|2|24 hours' weekly rest.|Working Time Regulations 1998 reg. 11
leave|2|5.6 weeks.|Working Time Regulations 1998 reg. 13
doc|1|General criminal law; Modern Slavery Act.|
live|1|Accommodation offset rules; living in may be agreed.|
mob|1|May change employer within the six-month visa, which cannot be extended.|Immigration Rules Appendix ODW
fee|2|Employment agencies may not charge work-seekers fees.|Conduct of Employment Agencies Regulations 2003
agen|1|Employment Agency Standards inspectorate; no licensing for domestic work.|
insp|1|Complaint-based.|
disp|2|Employment tribunals.|
soc|2|National Insurance, including maternity pay.|
viol|2|Modern Slavery Act 2015; C190 ratified.|Modern Slavery Act 2015 s. 1
org|2|May form and join unions.|""",
"US": """cov|2|Federal minimum wage and overtime cover domestic workers since 1974; live-in workers are exempt from overtime. Several states have domestic workers' bills of rights.|Fair Labor Standards Act 29 U.S.C. 206(f), 213(b)(21)
con|2|A-3 and G-5 visas need a written contract in a language the worker understands.|TVPRA 2008 s. 203
wage|2|Federal minimum wage applies.|29 U.S.C. 206(f)
pay|1|Record-keeping duties.|29 C.F.R. 552
hrs|1|Overtime pay, but live-in workers exempt.|29 U.S.C. 213(b)(21)
rest|0|No federal weekly rest (some states, e.g. New York, provide 24 hours).|
leave|0|No federal paid leave.|
doc|2|Document servitude is a federal offence.|18 U.S.C. 1592
live|0|No federal rule.|
mob|0|A-3 and G-5 visas tied to one employer.|
fee|1|Recruitment fee bans for some visas and federal contractors.|
agen|0|No federal licensing.|
insp|1|Complaint-based.|
disp|2|Courts and the Wage and Hour Division.|
soc|2|Social Security covers domestic employees above an earnings threshold.|
viol|2|Trafficking Victims Protection Act.|
org|0|National Labor Relations Act excludes domestic service.|29 U.S.C. 152(3)""",
"CA": """cov|2|Provincial employment standards cover domestic workers in most provinces (Ontario as reference).|Employment Standards Act 2000 (Ontario)
con|2|Employment contract required for the work permit.|Immigration and Refugee Protection Regulations s. 209.2
wage|2|Provincial minimum wage applies.|
pay|2|Wage payment rules apply.|
hrs|1|Overtime rules apply with some provincial exceptions.|
rest|2|24 hours' weekly rest (Ontario).|
leave|2|Two weeks.|
doc|2|Employers may not take a foreign worker's passport or work permit (Ontario).|Employment Protection for Foreign Nationals Act 2009
live|2|Live-in requirement removed in 2014.|
mob|1|Caregiver pilots gave occupation-specific permits; other streams are employer-specific.|
fee|2|Employers must ensure no recruitment fees are charged; provincial bans.|IRPR s. 209.2(1)(a)
agen|1|Licensing in some provinces.|
insp|1|Complaint-based, with some proactive inspection.|
disp|2|Employment standards officers and tribunals.|
soc|2|Canada Pension Plan and Employment Insurance.|
viol|1|C190 ratified; provincial law.|
org|1|Some provinces exclude domestic workers from labor relations law.|Labour Relations Act (Ontario) s. 3(a)""",
"AR": """cov|2|Dedicated statute with rights equal to the general labor law.|Law 26.844 (2013)
con|1|Registration required; written contract not required.|Law 26.844
wage|2|Minimum pay set by the National Commission for Private Household Work.|Law 26.844 art. 18
pay|2|Monthly payment with receipt.|Law 26.844
hrs|2|8 hours a day, 48 a week.|Law 26.844 art. 14
rest|2|35 hours' weekly rest.|Law 26.844 art. 14
leave|2|14-35 days.|Law 26.844 art. 29
doc|1|General law.|
live|2|Live-in or live-out; private and decent accommodation.|Law 26.844 art. 14
mob|2|Migration status not tied to one employer.|Law 25.871
fee|1|Not determined.|
agen|1|Agencies jointly liable.|Law 26.844
insp|1|Inspection limited.|
disp|2|Labor tribunal for private household work.|Law 26.844 art. 51
soc|2|Social security, maternity and work injury.|Law 26.844
viol|2|C190 ratified.|
org|2|May form and join unions.|""",
"ZA": """cov|2|Basic Conditions of Employment Act and a sectoral determination for domestic work.|BCEA 1997; Sectoral Determination 7 (2002)
con|2|Written particulars of employment.|Sectoral Determination 7 cl. 9
wage|2|National minimum wage applies in full since 2022.|National Minimum Wage Act 2018
pay|2|Pay slip; deductions limited.|Sectoral Determination 7
hrs|2|45 hours a week.|Sectoral Determination 7 cl. 10
rest|2|36 consecutive hours.|Sectoral Determination 7 cl. 15
leave|2|Three weeks.|Sectoral Determination 7 cl. 19
doc|1|General law.|
live|1|Accommodation offsets regulated.|Sectoral Determination 7
mob|1|Work visas tied to the employer.|
fee|2|Agencies may not charge work-seekers.|Employment Services Act 2014 s. 15
agen|1|Registered agencies.|Employment Services Act 2014
insp|2|Inspectors may enter a private home with consent or a court order.|BCEA ss. 65-66
disp|2|CCMA.|
soc|2|Unemployment insurance since 2003; work-injury compensation since 2020.|Mahlangu v Minister of Labour 2021 (CC)
viol|2|C190 ratified; Protection from Harassment Act.|
org|2|May form and join unions.|""",
}
