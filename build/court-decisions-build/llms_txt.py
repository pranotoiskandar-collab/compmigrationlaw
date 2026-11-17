SITE='/mnt/project-files/theimr-site'
t='''# Institute for Migrant Rights (IMR)

> IMR (West Java, Indonesia) runs a free Legal Clinic for migrant workers and publishes open research datasets on migration law and migrant workers' rights, built for empirical legal scholarship, statistical analysis in law, law and economics, comparative law and socio-legal research, and for advocacy. Most pages are in English and Indonesian.

## Datasets and comparisons
- [Migration Jurisprudence from the South](https://theimr.org/court-decisions/): about 500 court decisions on migrants from national, regional and international courts, led by Asia, Africa, the Middle East and Latin America; coded variables (type of case, outcome, arguments, follow-up), plain-language summaries in English and Indonesian. Data: https://theimr.org/court-decisions/data/decisions.csv
- [All decisions, one page each](https://theimr.org/court-decisions/d/)
- [Migration Law Atlas](https://theimr.org/migration-law/): global, regional and national migration law, ratifications, country profiles
- [Farmworker Norms Atlas](https://theimr.org/atlas/): ranked international, regional and national norms on farm work
- [Gulf States](https://theimr.org/gcc/): migration and labor laws in comparison, six Gulf states
- [East Asia](https://theimr.org/east-asia/): Taiwan, South Korea, Hong Kong and Japan
- [Countries of Origin](https://theimr.org/countries-of-origin/): emigration and protection law in eight countries of origin
- [Hate Speech and Voting](https://theimr.org/hate-speech-voting/): party hate speech, votes and non-citizen protection in 34 democracies
- [Government Hate Speech](https://theimr.org/government-hate-speech/): research project on hateful speech by officials

## Help for migrant workers
- [Legal Clinic](https://theimr.org/legal-clinic/): submit a rights communication
- [Find legal help](https://theimr.org/legal-help/): map and directory of free legal help

## About
- [People](https://theimr.org/people.html)
- [Publications: Indonesian Journal of International & Comparative Law and IMR Press books](https://theimr.org/publications.html)
- [Contact](https://theimr.org/contact.html)

Summaries are for research and advocacy, not legal advice. Cite the dataset name, version and URL.
'''
open(SITE+'/llms.txt','w').write(t); print('llms.txt written')
