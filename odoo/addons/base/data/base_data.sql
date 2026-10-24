-------------------------------------------------------------------------
-- Pure SQL (UUID primary keys — must match odoo.orm.bootstrap_ids)
-------------------------------------------------------------------------

CREATE TABLE ir_actions (
  id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid()
);
CREATE TABLE ir_act_window (primary key(id)) INHERITS (ir_actions);
CREATE TABLE ir_act_report_xml (primary key(id)) INHERITS (ir_actions);
CREATE TABLE ir_act_url (primary key(id)) INHERITS (ir_actions);
CREATE TABLE ir_act_server (primary key(id)) INHERITS (ir_actions);
CREATE TABLE ir_act_client (primary key(id)) INHERITS (ir_actions);

CREATE TABLE res_users (
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    -- No FK references below, will be added later by ORM
    company_id UUID,
    partner_id UUID,
    active boolean default True,
    create_date timestamp without time zone,
    login varchar(64) NOT NULL UNIQUE,
    password varchar default null
);

CREATE TABLE res_groups (
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    name jsonb NOT NULL
);

CREATE TABLE ir_module_category (
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    create_uid UUID,
    create_date timestamp without time zone,
    write_date timestamp without time zone,
    write_uid UUID,
    parent_id UUID REFERENCES ir_module_category ON DELETE SET NULL,
    name jsonb NOT NULL
);

CREATE TABLE ir_module_module (
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    create_uid UUID,
    create_date timestamp without time zone,
    write_date timestamp without time zone,
    write_uid UUID,
    website character varying,
    summary jsonb,
    name character varying NOT NULL,
    author character varying,
    icon varchar,
    state character varying(16),
    latest_version character varying,
    shortdesc jsonb,
    category_id UUID REFERENCES ir_module_category ON DELETE SET NULL,
    description jsonb,
    application boolean default False,
    demo boolean default False,
    test_data boolean default False,
    web boolean DEFAULT FALSE,
    license character varying(32),
    sequence integer DEFAULT 100,
    auto_install boolean default False,
    to_buy boolean default False
);

CREATE TABLE ir_module_module_dependency (
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    name character varying,
    module_id UUID REFERENCES ir_module_module ON DELETE cascade,
    auto_install_required boolean DEFAULT true
);

CREATE TABLE ir_model_data (
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    create_uid UUID,
    create_date timestamp without time zone DEFAULT (now() at time zone 'UTC'),
    write_date timestamp without time zone DEFAULT (now() at time zone 'UTC'),
    write_uid UUID,
    res_id UUID,
    noupdate boolean DEFAULT False,
    name varchar NOT NULL,
    module varchar NOT NULL,
    model varchar NOT NULL
);

CREATE TABLE res_currency (
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    name varchar NOT NULL,
    symbol varchar NOT NULL
);

CREATE TABLE res_company (
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    name varchar NOT NULL,
    partner_id UUID,
    currency_id UUID,
    sequence integer,
    create_date timestamp without time zone
);

CREATE TABLE res_partner (
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID,
    create_date timestamp without time zone,
    name varchar
);


---------------------------------
-- Default data
---------------------------------
insert into res_currency (id, name, symbol) VALUES ('00000000-0000-0000-0000-000000000010', 'USD', '$');
insert into ir_model_data (name, module, model, noupdate, res_id) VALUES ('USD', 'base', 'res.currency', true, '00000000-0000-0000-0000-000000000010');

insert into res_company (id, name, partner_id, currency_id, sequence, create_date) VALUES ('00000000-0000-0000-0000-000000000012', 'My Company', '00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000010', 10, now() at time zone 'UTC');
insert into ir_model_data (name, module, model, noupdate, res_id) VALUES ('main_company', 'base', 'res.company', true, '00000000-0000-0000-0000-000000000012');

insert into res_partner (id, name, company_id, create_date) VALUES ('00000000-0000-0000-0000-000000000011', 'My Company', '00000000-0000-0000-0000-000000000012', now() at time zone 'UTC');
insert into ir_model_data (name, module, model, noupdate, res_id) VALUES ('main_partner', 'base', 'res.partner', true, '00000000-0000-0000-0000-000000000011');

insert into res_users (id, login, password, active, partner_id, company_id, create_date) VALUES ('00000000-0000-0000-0000-000000000001', '__system__', NULL, false, '00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000012', now() at time zone 'UTC');
insert into ir_model_data (name, module, model, noupdate, res_id) VALUES ('user_root', 'base', 'res.users', true, '00000000-0000-0000-0000-000000000001');

insert into res_groups (id, name) VALUES ('00000000-0000-0000-0000-000000000020', '{"en_US": "Employee"}');
insert into ir_model_data (name, module, model, noupdate, res_id) VALUES ('group_user', 'base', 'res.groups', true, '00000000-0000-0000-0000-000000000020');
