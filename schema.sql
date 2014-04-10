create table doc (
  doc_id integer primary key autoincrement,
  title text not null,
  body text not null,
  url text,
  published_date date
);

create table label (
  label_id integer primary key autoincrement,
  tag text unique not null,
  description text
);

create unique index label_tag_idx on label(tag);

create table doc_label (
  doc_label_id integer primary key autoincrement,
  doc_id integer not null,
  label_id integer not null,
  foreign key(doc_id) references doc(doc_id),
  foreign key(label_id) references label(label_id),
  unique(doc_id, label_id)
);

create index doc_label_idx on doc_label(doc_id);
create index label_doc_idx on doc_label(label_id);

create table doc_relevance (
  doc_id integer primary key not null,
  relevance float not null,
  foreign key(doc_id) references doc(doc_id)
);

create index doc_relevance_idx on doc_relevance(relevance desc);

create table meta (
  meta_id integer primary key autoincrement,
  key text unique not null,
  value text
);

create unique index meta_key_idx on meta(key);
