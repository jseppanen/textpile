alter table doc_relevance rename to doc_relevance_old;

create table doc_relevance (
  doc_id integer primary key not null,
  relevance float not null,
  explain_json text,
  foreign key(doc_id) references doc(doc_id)
);

insert into doc_relevance
  select doc_id, relevance, null from doc_relevance_old;

drop index doc_relevance_idx;
create index doc_relevance_idx on doc_relevance(relevance desc);

drop table doc_relevance_old;
