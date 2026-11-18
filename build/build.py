# Builds index.html (the published app) from src/app.html.
# Needs: cd build && npm install   (brings @supabase/supabase-js, which is inlined into the page)
import datetime, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl = open(os.path.join(ROOT, 'src', 'app.html'), encoding='utf-8').read()
lib = open(os.path.join(ROOT, 'build', 'node_modules', '@supabase', 'supabase-js', 'dist', 'umd', 'supabase.js'), encoding='utf-8').read()
assert '</script' not in lib.lower()
ver = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M')
out = tpl.replace('/*__SUPABASE_LIB__*/', lib).replace('__VERSION__', ver)
open(os.path.join(ROOT, 'version.txt'), 'w').write(ver + '\n')
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(out)
print('built', ver, len(out.encode()))
