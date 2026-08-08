import zipfile
from pathlib import Path
p=Path('templates/civil_contract')
for f in sorted(p.glob('*.docx')):
    print('Scanning %s' % f.name)
    try:
        with zipfile.ZipFile(f) as z:
            xml=z.read('word/document.xml').decode('utf-8')
    except Exception as e:
        print('  ERROR reading', e)
        continue
    lines=xml.splitlines()
    for i,l in enumerate(lines,1):
        if '{{' in l or '}}' in l or '{%' in l or '%}' in l or '[[' in l or ']]' in l:
            print('  %s: %s' % (i, l.strip()))
