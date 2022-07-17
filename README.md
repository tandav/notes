# notes

## archive

```sql
select n.id, n.url
from note n
join notes_tags nt on n.id = nt.note_id
join tag t on t.id = nt.tag_id
where t.name != 'archive' and n.url like '% %'
```
