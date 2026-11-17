import csv,re
JP=re.compile(r'退去|難民|在留|入国|出入国|上陸|旅券|査証|国籍|帰化|外国人|仮放免|収容|技能実習|人身取引|被爆者|永住|強制送還|逃亡犯罪人')
KR=re.compile(r'난민|출입국|강제퇴거|체류|사증|귀화|국적|외국인|고용허가|입국|인신매매|이주|결혼이민|재외동포|보호명령|여권|인신보호|산업기술연수|산업연수')
KR_NO=re.compile(r'제4조 제1항|제4조의2|검사증|노숙|카지노|재산세|외국환|출국금지|출국정지|여권의 사용제한|국가보안법')
def clean(t): return re.sub(r'\s*\((原審|差戻前).*?\)$','',t).strip()
def level(x):
    c=x['court']
    if any(k in c for k in ('最高裁','대법원','헌법재판소','Court of Final Appeal','終審法院')): return 'apex'
    if any(k in c for k in ('高等裁判所','고등법원','Court of Appeal','中級法院')): return 'appeal'
    return ''
def site(x):
    t=clean(x['title']); j=x['jurisdiction']
    if x['farm_terms']: return True
    if not level(x): return False
    if j=='JP': return bool(JP.search(t))
    if j=='KR': return bool(KR.search(t)) and not KR_NO.search(t)
    return True
