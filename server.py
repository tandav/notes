import datetime
import json
from string import Template
from fastapi import FastAPI
from fastapi import Form
from fastapi.responses import HTMLResponse
from database import Database

db = Database('notes.db')
app = FastAPI()

header = '''\
<span class='header'>
<a class='link' href='/'>HOME</a>
<a class='link' href='/create'>NEW NOTE</a>
</span>
'''

css = '''
<style>
.header .link {
    margin-right: 20px;
}
body {
    background-color: rgba(0,0,0, 0.04);
    font-family: monospace;

}
.note {
    padding: 10px;
    border: 1px solid rgba(0,0,0,0.5);
    box-shadow: 2px 2px;
    border-radius: 3px;
    background: white;
}
#text {
    width: 300px;
    height: 75px;
    font-family: monospace;
}
</style>
'''


@app.get('/', response_class=HTMLResponse)
async def root():
    html = ''.join(f'''
    <pre class='note'>
    {{'id': {i}, 'timestamp': '{t}'}}
    ----------------------------------------------------
    {text}
    </pre>
    '''
    for i, t, text in db.get_all()
    )
    return header + html + css

@app.get('/create', response_class=HTMLResponse)
async def create():
    html = '''
    <h1/>create note<h1>
    <form action='/note', method='post'>
        <input type="text" id="text" name="text">
        <input type="submit" value="create">
    </form>
    '''
    return header + html + css


@app.post('/note')
async def save_note(text: str = Form(...)):
    db.insert(text)
    print(text)
    return 'note saved'
