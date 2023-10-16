Table 1: resources

create table
  public.resources (
    id bigint generated by default as identity,
    red_ml integer not null default 0,
    blue_ml integer not null default 0,
    green_ml integer not null default 0,
    gold integer not null default 0,
    dark_ml integer not null default 0,
    constraint resources_pkey primary key (id)
  ) tablespace pg_default;


Table 2: potions

create table
  public.potions (
    id bigint generated by default as identity,
    sku text null,
    name text null,
    potion_type text null,
    price integer null,
    inventory integer null default 0,
    red integer null,
    green integer null,
    blue integer null,
    dark integer null default 0,
    constraint potions_pkey primary key (id),
    constraint potions_id_key unique (id)
  ) tablespace pg_default;


Table 3: customer_carts

create table
  public.customer_carts (
    id bigint generated by default as identity,
    customer_name text null,
    paid boolean null default false,
    created_at timestamp with time zone not null default (now() at time zone 'pst'::text),
    constraint cutsomer_carts2_pkey primary key (id)
  ) tablespace pg_default;


Table 4: cart_items

create table
  public.customer_carts (
    id bigint generated by default as identity,
    customer_name text null,
    paid boolean null default false,
    created_at timestamp with time zone not null default (now() at time zone 'pst'::text),
    constraint cutsomer_carts2_pkey primary key (id)
  ) tablespace pg_default;