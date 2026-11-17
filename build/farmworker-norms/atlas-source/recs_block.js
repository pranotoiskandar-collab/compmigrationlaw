// What supervisory bodies asked each state to do, and whether it has. [body, year, what was asked, status, note]
// Status: done = implemented, part = partly, open = not implemented. IMR assessment, October 2026; check the source before citing.
const RECS = {
"Indonesia":[
 ["Universal Periodic Review (4th cycle)",2022,"Ratify ILO C189 on domestic workers and adopt a domestic workers protection law","part","The Domestic Workers Protection Law passed the DPR in April 2026; C189 is not yet ratified."],
 ["UN Committee on Migrant Workers",2017,"Bring national law fully in line with the ICRMW, including protection of foreign migrant workers in Indonesia and of migrants' families","part","Law 18/2017 strengthened protection of Indonesians abroad; protection of foreign workers in Indonesia is still thin."],
 ["Universal Periodic Review",2022,"Ratify the 1951 Refugee Convention","open","Refugees remain under Presidential Regulation 125/2016 with no right to work."],
 ["UN treaty bodies (several)",2013,"Accept individual complaints procedures (for example the ICCPR Optional Protocol)","open","Indonesia has accepted no individual complaints procedure, which is why the Clinic routes cases to Special Procedures."]],
"Philippines":[
 ["UN Committee on Migrant Workers",2023,"Strengthen regulation of recruitment fees and protect workers from debt bondage","part","The Department of Migrant Workers Act (2021) consolidated agencies; zero-fee policies are not consistently enforced."],
 ["ILO Committee of Experts (C87)",2023,"Lower union registration thresholds and stop violence against trade unionists","part","An ILO high-level tripartite mission visited in 2023; killings of union organizers remain a concern."]],
"Thailand":[
 ["Universal Periodic Review",2021,"Ratify ILO C87 and C98 so that migrant workers can form and lead unions","open","The Labour Relations Act still bars non-Thai nationals from founding unions."],
 ["ILO Committee of Experts (P29)",2023,"Ensure effective labor inspection and remedies for migrant workers in fishing and agriculture","part","Forced labor offense added in 2019; inspections in agriculture remain limited."]],
"Malaysia":[
 ["Universal Periodic Review",2024,"Ratify the 1951 Refugee Convention and the ICRMW","open","Neither ratified."],
 ["ILO Committee of Experts (C29/P29)",2023,"Prohibit passport retention and recruitment fees charged to migrant workers","part","The 2022 Employment Act amendments added a forced labor offense; passport retention persists on plantations."]],
"United States of America":[
 ["Universal Periodic Review",2020,"Ratify the ICESCR","open","Signed in 1977; never ratified."],
 ["ILO Committee on Freedom of Association (Case No. 2227)",2003,"Address the effect of Hoffman Plastic on the protection of undocumented workers against anti-union discrimination","open","Back pay remains unavailable to undocumented workers under federal labor law."]],
"United Kingdom":[
 ["UN Committee on Economic, Social and Cultural Rights",2016,"Incorporate Covenant rights into domestic law","open","No incorporating statute."],
 ["UK government review of the Seasonal Worker visa",2023,"Strengthen protections against debt and exploitation for seasonal agricultural workers","part","Guidance on recruitment fees tightened; workers remain tied to scheme operators."]],
"Italy":[
 ["ILO Committee of Experts (C81/C129)",2022,"Increase labor inspection in agriculture and protect workers who report exploitation regardless of status","part","Inspection capacity grew after 2016; undocumented workers who report still risk expulsion."],
 ["UN Special Rapporteur on contemporary forms of slavery",2018,"Address caporalato through regularization and housing for farmworkers","part","A 2020 regularization drew 207,000 applications, most for domestic work rather than agriculture."]],
"Spain":[
 ["UN Special Rapporteur on extreme poverty",2020,"Improve living conditions in migrant farmworker settlements in Huelva","open","Informal settlements remain."]],
"Brazil":[
 ["Inter-American Court (Hacienda Brasil Verde)",2016,"Reopen investigations and ensure slave labor crimes are not time-barred","part","Investigations were reopened; the Court continues to supervise compliance."]],
"Mexico":[
 ["UN Committee on Migrant Workers",2017,"End detention of migrants, especially children, and investigate abuses against migrants in transit","part","Detention of children was banned in law in 2020; detention of adults continues."]],
"India":[
 ["ILO Committee of Experts (C29)",2022,"Improve identification, release and rehabilitation of bonded laborers","part","Rehabilitation scheme revised in 2016; numbers identified remain low."]],
"South Africa":[
 ["UN Committee on Economic, Social and Cultural Rights",2018,"Protect farm dwellers from eviction and extend minimum wage parity to farmworkers","part","Farm minimum wage raised to the national rate in 2022; evictions continue."]],
"Canada":[
 ["ILO Committee on Freedom of Association (Case No. 2704)",2010,"Ensure Ontario agricultural workers can bargain collectively","open","The Agricultural Employees Protection Act still gives no duty to bargain."],
 ["UN Special Rapporteur on contemporary forms of slavery",2023,"Move away from employer-specific work permits for temporary foreign workers","open","Open permits exist only for workers who show abuse."]],
"Australia":[
 ["Fair Work Commission, on an application by the Australian Workers' Union",2021,"Set a floor under piece rates in horticulture","done","Minimum piece-rate guarantee in the Horticulture Award from 2022."]],
"Germany":[
 ["UN Committee on Economic, Social and Cultural Rights",2018,"Ensure seasonal agricultural workers have health insurance and decent housing","part","Short-term employment rules still let employers avoid social insurance for up to 70 days."]],
"New Zealand":[
 ["Human Rights Commission inquiry into the RSE scheme",2022,"Strengthen the rights of Recognised Seasonal Employer workers, including to change employer","part","Some changes made to pastoral care rules; workers remain tied to employers."]],
"Kenya":[
 ["ILO Committee of Experts (C129)",2021,"Increase the number of labor inspectors and visits to agricultural undertakings","open","Inspection capacity remains low."]],
"France":[
 ["UN Committee on Economic, Social and Cultural Rights",2016,"Combat abuses of posted workers and seasonal migrants in agriculture","part","Controls on fraudulent postings increased."]]
};
