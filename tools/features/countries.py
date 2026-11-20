# Country table for the comparison, timeline and coverage pages.
# ISO 3166-1 alpha-2, numeric (as used by the Natural Earth / world-atlas map), English name, Indonesian name,
# and other spellings found in the data (NORMLEX/UN names in data/atlas/ratifications.csv).
# Places too small for the 1:110m map get a dot at (lon, lat).
C = [
 ("AF","004","Afghanistan","Afganistan"),("AL","008","Albania","Albania"),("DZ","012","Algeria","Aljazair"),
 ("AD","020","Andorra","Andorra"),("AO","024","Angola","Angola"),("AG","028","Antigua and Barbuda","Antigua dan Barbuda"),
 ("AR","032","Argentina","Argentina"),("AM","051","Armenia","Armenia"),("AU","036","Australia","Australia"),
 ("AT","040","Austria","Austria"),("AZ","031","Azerbaijan","Azerbaijan"),("BS","044","Bahamas","Bahama"),
 ("BH","048","Bahrain","Bahrain"),("BD","050","Bangladesh","Bangladesh"),("BB","052","Barbados","Barbados"),
 ("BY","112","Belarus","Belarus"),("BE","056","Belgium","Belgia"),("BZ","084","Belize","Belize"),
 ("BJ","204","Benin","Benin"),("BT","064","Bhutan","Bhutan"),("BO","068","Bolivia","Bolivia"),
 ("BA","070","Bosnia and Herzegovina","Bosnia dan Herzegovina"),("BW","072","Botswana","Botswana"),
 ("BR","076","Brazil","Brasil"),("BN","096","Brunei","Brunei"),("BG","100","Bulgaria","Bulgaria"),
 ("BF","854","Burkina Faso","Burkina Faso"),("BI","108","Burundi","Burundi"),("CV","132","Cabo Verde","Tanjung Verde"),
 ("KH","116","Cambodia","Kamboja"),("CM","120","Cameroon","Kamerun"),("CA","124","Canada","Kanada"),
 ("CF","140","Central African Republic","Republik Afrika Tengah"),("TD","148","Chad","Chad"),("CL","152","Chile","Chili"),
 ("CN","156","China","Tiongkok"),("CO","170","Colombia","Kolombia"),("KM","174","Comoros","Komoro"),
 ("CG","178","Congo","Kongo"),("CD","180","DR Congo","Republik Demokratik Kongo"),("CK","184","Cook Islands","Kepulauan Cook"),
 ("CR","188","Costa Rica","Kosta Rika"),("HR","191","Croatia","Kroasia"),("CU","192","Cuba","Kuba"),
 ("CY","196","Cyprus","Siprus"),("CZ","203","Czechia","Ceko"),("CI","384","Côte d'Ivoire","Pantai Gading"),
 ("DK","208","Denmark","Denmark"),("DJ","262","Djibouti","Djibouti"),("DM","212","Dominica","Dominika"),
 ("DO","214","Dominican Republic","Republik Dominika"),("EC","218","Ecuador","Ekuador"),("EG","818","Egypt","Mesir"),
 ("SV","222","El Salvador","El Salvador"),("GQ","226","Equatorial Guinea","Guinea Khatulistiwa"),("ER","232","Eritrea","Eritrea"),
 ("EE","233","Estonia","Estonia"),("SZ","748","Eswatini","Eswatini"),("ET","231","Ethiopia","Etiopia"),
 ("FJ","242","Fiji","Fiji"),("FI","246","Finland","Finlandia"),("FR","250","France","Prancis"),
 ("GA","266","Gabon","Gabon"),("GM","270","Gambia","Gambia"),("GE","268","Georgia","Georgia"),
 ("DE","276","Germany","Jerman"),("GH","288","Ghana","Ghana"),("GR","300","Greece","Yunani"),
 ("GD","308","Grenada","Grenada"),("GT","320","Guatemala","Guatemala"),("GN","324","Guinea","Guinea"),
 ("GW","624","Guinea-Bissau","Guinea-Bissau"),("GY","328","Guyana","Guyana"),("HT","332","Haiti","Haiti"),
 ("HN","340","Honduras","Honduras"),("HK","344","Hong Kong SAR","Hong Kong SAR"),("HU","348","Hungary","Hungaria"),
 ("IS","352","Iceland","Islandia"),("IN","356","India","India"),("ID","360","Indonesia","Indonesia"),
 ("IR","364","Iran","Iran"),("IQ","368","Iraq","Irak"),("IE","372","Ireland","Irlandia"),
 ("IL","376","Israel","Israel"),("IT","380","Italy","Italia"),("JM","388","Jamaica","Jamaika"),
 ("JP","392","Japan","Jepang"),("JO","400","Jordan","Yordania"),("KZ","398","Kazakhstan","Kazakhstan"),
 ("KE","404","Kenya","Kenya"),("KW","414","Kuwait","Kuwait"),("KG","417","Kyrgyzstan","Kirgizstan"),
 ("LA","418","Laos","Laos"),("LV","428","Latvia","Latvia"),("LB","422","Lebanon","Lebanon"),
 ("LS","426","Lesotho","Lesotho"),("LR","430","Liberia","Liberia"),("LY","434","Libya","Libya"),
 ("LI","438","Liechtenstein","Liechtenstein"),("LT","440","Lithuania","Lituania"),("LU","442","Luxembourg","Luksemburg"),
 ("MO","446","Macao SAR","Makau SAR"),("MG","450","Madagascar","Madagaskar"),("MW","454","Malawi","Malawi"),
 ("MY","458","Malaysia","Malaysia"),("MV","462","Maldives","Maladewa"),("ML","466","Mali","Mali"),
 ("MT","470","Malta","Malta"),("MH","584","Marshall Islands","Kepulauan Marshall"),("MR","478","Mauritania","Mauritania"),
 ("MU","480","Mauritius","Mauritius"),("MX","484","Mexico","Meksiko"),("MC","492","Monaco","Monako"),
 ("MN","496","Mongolia","Mongolia"),("ME","499","Montenegro","Montenegro"),("MA","504","Morocco","Maroko"),
 ("MZ","508","Mozambique","Mozambik"),("MM","104","Myanmar","Myanmar"),("NA","516","Namibia","Namibia"),
 ("NP","524","Nepal","Nepal"),("NL","528","Netherlands","Belanda"),("NZ","554","New Zealand","Selandia Baru"),
 ("NI","558","Nicaragua","Nikaragua"),("NE","562","Niger","Niger"),("NG","566","Nigeria","Nigeria"),
 ("KP","408","North Korea","Korea Utara"),("MK","807","North Macedonia","Makedonia Utara"),("NO","578","Norway","Norwegia"),
 ("OM","512","Oman","Oman"),("PK","586","Pakistan","Pakistan"),("PW","585","Palau","Palau"),
 ("PS","275","Palestine","Palestina"),("PA","591","Panama","Panama"),("PG","598","Papua New Guinea","Papua Nugini"),
 ("PY","600","Paraguay","Paraguay"),("PE","604","Peru","Peru"),("PH","608","Philippines","Filipina"),
 ("PL","616","Poland","Polandia"),("PT","620","Portugal","Portugal"),("PR","630","Puerto Rico","Puerto Riko"),
 ("QA","634","Qatar","Qatar"),("KR","410","South Korea","Korea Selatan"),("MD","498","Moldova","Moldova"),
 ("RO","642","Romania","Rumania"),("RU","643","Russia","Rusia"),("RW","646","Rwanda","Rwanda"),
 ("KN","659","Saint Kitts and Nevis","Saint Kitts dan Nevis"),("LC","662","Saint Lucia","Saint Lucia"),
 ("VC","670","Saint Vincent and the Grenadines","Saint Vincent dan Grenadine"),("WS","882","Samoa","Samoa"),
 ("SM","674","San Marino","San Marino"),("ST","678","Sao Tome and Principe","Sao Tome dan Principe"),
 ("SA","682","Saudi Arabia","Arab Saudi"),("SN","686","Senegal","Senegal"),("RS","688","Serbia","Serbia"),
 ("SC","690","Seychelles","Seychelles"),("SL","694","Sierra Leone","Sierra Leone"),("SG","702","Singapore","Singapura"),
 ("SK","703","Slovakia","Slowakia"),("SI","705","Slovenia","Slovenia"),("SB","090","Solomon Islands","Kepulauan Solomon"),
 ("SO","706","Somalia","Somalia"),("ZA","710","South Africa","Afrika Selatan"),("SS","728","South Sudan","Sudan Selatan"),
 ("ES","724","Spain","Spanyol"),("LK","144","Sri Lanka","Sri Lanka"),("SD","729","Sudan","Sudan"),
 ("SR","740","Suriname","Suriname"),("SE","752","Sweden","Swedia"),("CH","756","Switzerland","Swiss"),
 ("SY","760","Syria","Suriah"),("TW","158","Taiwan","Taiwan"),("TJ","762","Tajikistan","Tajikistan"),
 ("TZ","834","Tanzania","Tanzania"),("TH","764","Thailand","Thailand"),("TL","626","Timor-Leste","Timor-Leste"),
 ("TG","768","Togo","Togo"),("TT","780","Trinidad and Tobago","Trinidad dan Tobago"),("TN","788","Tunisia","Tunisia"),
 ("TR","792","Türkiye","Turki"),("TM","795","Turkmenistan","Turkmenistan"),("UG","800","Uganda","Uganda"),
 ("UA","804","Ukraine","Ukraina"),("AE","784","United Arab Emirates","Uni Emirat Arab"),("GB","826","United Kingdom","Inggris Raya"),
 ("US","840","United States","Amerika Serikat"),("UY","858","Uruguay","Uruguay"),("UZ","860","Uzbekistan","Uzbekistan"),
 ("VU","548","Vanuatu","Vanuatu"),("VE","862","Venezuela","Venezuela"),("VN","704","Viet Nam","Vietnam"),
 ("YE","887","Yemen","Yaman"),("ZM","894","Zambia","Zambia"),("ZW","716","Zimbabwe","Zimbabwe"),
 ("EH","732","Western Sahara","Sahara Barat"),("GL","304","Greenland","Greenland"),
]
ALIASES = {
 "Bosnia and Herzegovina":"BA","Democratic Republic of the Congo":"CD","Democratic People's Republic of Korea":"KP",
 "Lao People's Democratic Republic":"LA","Republic of Korea":"KR","Republic of Moldova":"MD","Russian Federation":"RU",
 "State of Palestine":"PS","Syrian Arab Republic":"SY","United Republic of Tanzania":"TZ","United States of America":"US",
 "Viet Nam":"VN","Vietnam":"VN","Türkiye":"TR","Turkey":"TR","Eswatini":"SZ","Brunei Darussalam":"BN",
 "Hong Kong":"HK","Macao":"MO","Macau":"MO","Korea":"KR","South Korea":"KR","Iran (Islamic Republic of)":"IR",
 "Bolivia (Plurinational State of)":"BO","Venezuela (Bolivarian Republic of)":"VE","Czech Republic":"CZ",
}
# Places drawn as a dot because the 1:110m map leaves them out (lon, lat).
DOTS = {
 "SG":(103.82,1.35),"HK":(114.17,22.32),"MO":(112.6,21.2),"BH":(50.56,26.07),"MV":(73.22,3.2),"MT":(14.4,35.9),
 "MU":(57.55,-20.3),"AD":(1.52,42.5),"LI":(9.55,47.16),"MC":(7.42,43.74),"SM":(12.46,43.94),"BB":(-59.54,13.19),
 "AG":(-61.8,17.07),"DM":(-61.37,15.41),"GD":(-61.68,12.12),"KN":(-62.78,17.36),"LC":(-60.98,13.91),
 "VC":(-61.2,13.25),"CV":(-23.6,15.1),"KM":(43.87,-11.88),"ST":(6.61,0.19),"SC":(55.49,-4.68),
 "WS":(-172.1,-13.76),"PW":(134.58,7.51),"MH":(171.18,7.13),"CK":(-159.78,-21.24),
}
BY2 = {c[0]: c for c in C}
NUM = {c[1]: c[0] for c in C}
NAME = {c[2]: c[0] for c in C}
NAME.update(ALIASES)

def iso2(name):
    name = (name or '').strip()
    if len(name) == 2 and name.upper() in BY2:
        return name.upper()
    return NAME.get(name)
