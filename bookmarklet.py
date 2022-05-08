from urllib.parse import quote

href = '''
javascript:const title = encodeURI(document.title);
const url = location.href;window.location = `http://localhost:5003/new_note?text=${title}&url=${url}`;
void(0);
'''.replace('\n', '')
href = quote(href)

bookmarklet = f'<a href="{href}">bookmark</a>'

with open('README.md', 'w') as f:
    print(bookmarklet, file=f)
