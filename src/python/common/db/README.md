## Papers Table

### Sample queries

To count number of records by language:

```
select (metadata->>'language')::varchar as language, count(1) from papers \
  group by (metadata->>'language');
```

To count number of records by language in a limited range:

```
select (metadata->>'language')::varchar as language, count(1) from papers \
  inner join (select * from papers limit 2000) p on papers.id = p.id \
  group by (metadata->>'language');
```
