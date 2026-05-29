path = r'd:\Users\dibya\jyoti\face-detection-project\app.py'
marker = 'st.info("👈 Use the **sidebar** to navigate between modules")'
with open(path, encoding='utf-8') as f:
    content = f.read()
idx = content.find(marker)
print('Marker at index:', idx)
if idx >= 0:
    trimmed = content[:idx + len(marker)]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(trimmed)
    print('Done, chars:', len(trimmed))
else:
    print('MARKER NOT FOUND')
