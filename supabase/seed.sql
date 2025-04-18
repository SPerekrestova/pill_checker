SET session_replication_role = replica;

--
-- PostgreSQL database dump
--

-- Dumped from database version 15.8
-- Dumped by pg_dump version 15.8

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: audit_log_entries; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

INSERT INTO "auth"."audit_log_entries" ("instance_id", "id", "payload", "created_at", "ip_address") VALUES
	('00000000-0000-0000-0000-000000000000', '1846f32b-ba8a-4989-becd-989ef8400e04', '{"action":"user_signedup","actor_id":"ebf9ed03-50c3-41ee-8650-966848d095fd","actor_username":"svetlana.perekrestova2@gmail.com","actor_via_sso":false,"log_type":"team","traits":{"provider":"email"}}', '2025-03-03 23:53:46.922216+00', ''),
	('00000000-0000-0000-0000-000000000000', '4c819741-baa0-46a7-b1db-b1ed3298e613', '{"action":"login","actor_id":"ebf9ed03-50c3-41ee-8650-966848d095fd","actor_username":"svetlana.perekrestova2@gmail.com","actor_via_sso":false,"log_type":"account","traits":{"provider":"email"}}', '2025-03-03 23:53:46.927295+00', ''),
	('00000000-0000-0000-0000-000000000000', 'aa178f2f-b16a-43f9-aa80-9b666a29c1aa', '{"action":"login","actor_id":"ebf9ed03-50c3-41ee-8650-966848d095fd","actor_username":"svetlana.perekrestova2@gmail.com","actor_via_sso":false,"log_type":"account","traits":{"provider":"email"}}', '2025-03-03 23:53:50.588996+00', ''),
	('00000000-0000-0000-0000-000000000000', '4a3bc1aa-3ce6-4532-a636-01fe1a89d3c6', '{"action":"login","actor_id":"ebf9ed03-50c3-41ee-8650-966848d095fd","actor_username":"svetlana.perekrestova2@gmail.com","actor_via_sso":false,"log_type":"account","traits":{"provider":"email"}}', '2025-03-04 00:10:05.544377+00', ''),
	('00000000-0000-0000-0000-000000000000', '7eb7db41-69b3-4a58-8dc2-c15597a33629', '{"action":"login","actor_id":"ebf9ed03-50c3-41ee-8650-966848d095fd","actor_username":"svetlana.perekrestova2@gmail.com","actor_via_sso":false,"log_type":"account","traits":{"provider":"email"}}', '2025-03-04 00:14:25.162221+00', '');


--
-- Data for Name: flow_state; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: users; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

INSERT INTO "auth"."users" ("instance_id", "id", "aud", "role", "email", "encrypted_password", "email_confirmed_at", "invited_at", "confirmation_token", "confirmation_sent_at", "recovery_token", "recovery_sent_at", "email_change_token_new", "email_change", "email_change_sent_at", "last_sign_in_at", "raw_app_meta_data", "raw_user_meta_data", "is_super_admin", "created_at", "updated_at", "phone", "phone_confirmed_at", "phone_change", "phone_change_token", "phone_change_sent_at", "email_change_token_current", "email_change_confirm_status", "banned_until", "reauthentication_token", "reauthentication_sent_at", "is_sso_user", "deleted_at", "is_anonymous") VALUES
	('00000000-0000-0000-0000-000000000000', 'ebf9ed03-50c3-41ee-8650-966848d095fd', 'authenticated', 'authenticated', 'svetlana.perekrestova2@gmail.com', '$2a$10$uBTRP8Z7My/N7FhH9O2pd.dRKfBcgDSRjWoBxCzlPWhggt0Qe5wlO', '2025-03-03 23:53:46.923812+00', NULL, '', NULL, '', NULL, '', '', NULL, '2025-03-04 00:14:25.163384+00', '{"provider": "email", "providers": ["email"]}', '{"sub": "ebf9ed03-50c3-41ee-8650-966848d095fd", "email": "svetlana.perekrestova2@gmail.com", "email_verified": true, "phone_verified": false}', NULL, '2025-03-03 23:53:46.909559+00', '2025-03-04 00:14:25.16576+00', NULL, NULL, '', '', NULL, '', 0, NULL, '', NULL, false, NULL, false);


--
-- Data for Name: identities; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

INSERT INTO "auth"."identities" ("provider_id", "user_id", "identity_data", "provider", "last_sign_in_at", "created_at", "updated_at", "id") VALUES
	('ebf9ed03-50c3-41ee-8650-966848d095fd', 'ebf9ed03-50c3-41ee-8650-966848d095fd', '{"sub": "ebf9ed03-50c3-41ee-8650-966848d095fd", "email": "svetlana.perekrestova2@gmail.com", "email_verified": false, "phone_verified": false}', 'email', '2025-03-03 23:53:46.917651+00', '2025-03-03 23:53:46.917693+00', '2025-03-03 23:53:46.917693+00', '1b93dfc3-b0cc-4e67-986e-97e5b36a7d51');


--
-- Data for Name: instances; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: sessions; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

INSERT INTO "auth"."sessions" ("id", "user_id", "created_at", "updated_at", "factor_id", "aal", "not_after", "refreshed_at", "user_agent", "ip", "tag") VALUES
	('ea09feda-0c6b-4ebb-a24e-b8433a6bfc04', 'ebf9ed03-50c3-41ee-8650-966848d095fd', '2025-03-03 23:53:46.927659+00', '2025-03-03 23:53:46.927659+00', NULL, 'aal1', NULL, NULL, 'python-httpx/0.28.1', '172.18.0.14', NULL),
	('bf00cddc-04ba-4744-b962-bba8e1c0a21b', 'ebf9ed03-50c3-41ee-8650-966848d095fd', '2025-03-03 23:53:50.589743+00', '2025-03-03 23:53:50.589743+00', NULL, 'aal1', NULL, NULL, 'python-httpx/0.28.1', '172.18.0.14', NULL),
	('573c4079-1533-40d6-a40d-91c2ec456476', 'ebf9ed03-50c3-41ee-8650-966848d095fd', '2025-03-04 00:10:05.545408+00', '2025-03-04 00:10:05.545408+00', NULL, 'aal1', NULL, NULL, 'python-httpx/0.28.1', '172.18.0.14', NULL),
	('8bf03339-6895-4a03-bd58-01f7a08b5df7', 'ebf9ed03-50c3-41ee-8650-966848d095fd', '2025-03-04 00:14:25.163465+00', '2025-03-04 00:14:25.163465+00', NULL, 'aal1', NULL, NULL, 'python-httpx/0.28.1', '172.18.0.14', NULL);


--
-- Data for Name: mfa_amr_claims; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

INSERT INTO "auth"."mfa_amr_claims" ("session_id", "created_at", "updated_at", "authentication_method", "id") VALUES
	('ea09feda-0c6b-4ebb-a24e-b8433a6bfc04', '2025-03-03 23:53:46.931373+00', '2025-03-03 23:53:46.931373+00', 'password', '68c0fb2b-12da-4fe3-92c5-7d934d8643fb'),
	('bf00cddc-04ba-4744-b962-bba8e1c0a21b', '2025-03-03 23:53:50.591572+00', '2025-03-03 23:53:50.591572+00', 'password', 'fcec90ec-6bad-4d4b-aaa2-13fdb960570b'),
	('573c4079-1533-40d6-a40d-91c2ec456476', '2025-03-04 00:10:05.547764+00', '2025-03-04 00:10:05.547764+00', 'password', 'cc0d0aea-ddf5-4ba4-9cb9-e11b48626136'),
	('8bf03339-6895-4a03-bd58-01f7a08b5df7', '2025-03-04 00:14:25.166061+00', '2025-03-04 00:14:25.166061+00', 'password', 'f956f751-4880-4b3c-abb9-16d0506ed844');


--
-- Data for Name: mfa_factors; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: mfa_challenges; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: one_time_tokens; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

INSERT INTO "auth"."refresh_tokens" ("instance_id", "id", "token", "user_id", "revoked", "created_at", "updated_at", "parent", "session_id") VALUES
	('00000000-0000-0000-0000-000000000000', 1, 'FTapsfYXBlRBGxsI628v7g', 'ebf9ed03-50c3-41ee-8650-966848d095fd', false, '2025-03-03 23:53:46.929169+00', '2025-03-03 23:53:46.929169+00', NULL, 'ea09feda-0c6b-4ebb-a24e-b8433a6bfc04'),
	('00000000-0000-0000-0000-000000000000', 2, 'ZVWp8FV4t9oJHR2ThB7J0A', 'ebf9ed03-50c3-41ee-8650-966848d095fd', false, '2025-03-03 23:53:50.590469+00', '2025-03-03 23:53:50.590469+00', NULL, 'bf00cddc-04ba-4744-b962-bba8e1c0a21b'),
	('00000000-0000-0000-0000-000000000000', 3, 'xVHm6tnOJLuBCbN34gSB9g', 'ebf9ed03-50c3-41ee-8650-966848d095fd', false, '2025-03-04 00:10:05.54641+00', '2025-03-04 00:10:05.54641+00', NULL, '573c4079-1533-40d6-a40d-91c2ec456476'),
	('00000000-0000-0000-0000-000000000000', 4, 'dLyA86gx8YxWWOBrEDNQbQ', 'ebf9ed03-50c3-41ee-8650-966848d095fd', false, '2025-03-04 00:14:25.164537+00', '2025-03-04 00:14:25.164537+00', NULL, '8bf03339-6895-4a03-bd58-01f7a08b5df7');


--
-- Data for Name: sso_providers; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: saml_providers; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: saml_relay_states; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: sso_domains; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: key; Type: TABLE DATA; Schema: pgsodium; Owner: supabase_admin
--



--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."profiles" ("id", "username", "bio", "created_at", "updated_at") VALUES
	('ebf9ed03-50c3-41ee-8650-966848d095fd', 'Svetlana.Perekrestova2', NULL, '2025-03-03 23:53:46.947059', '2025-03-03 23:53:46.947164');


--
-- Data for Name: medications; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: buckets; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--

INSERT INTO "storage"."buckets" ("id", "name", "owner", "created_at", "updated_at", "public", "avif_autodetection", "file_size_limit", "allowed_mime_types", "owner_id") VALUES
	('scans', 'scans', NULL, '2025-03-03 23:50:07.495531+00', '2025-03-03 23:50:07.495531+00', true, false, NULL, NULL, NULL);


--
-- Data for Name: objects; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--



--
-- Data for Name: prefixes; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--



--
-- Data for Name: s3_multipart_uploads; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--



--
-- Data for Name: s3_multipart_uploads_parts; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--



--
-- Data for Name: hooks; Type: TABLE DATA; Schema: supabase_functions; Owner: supabase_functions_admin
--



--
-- Data for Name: secrets; Type: TABLE DATA; Schema: vault; Owner: supabase_admin
--



--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE SET; Schema: auth; Owner: supabase_auth_admin
--

SELECT pg_catalog.setval('"auth"."refresh_tokens_id_seq"', 4, true);


--
-- Name: key_key_id_seq; Type: SEQUENCE SET; Schema: pgsodium; Owner: supabase_admin
--

SELECT pg_catalog.setval('"pgsodium"."key_key_id_seq"', 1, false);


--
-- Name: medications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."medications_id_seq"', 1, false);


--
-- Name: hooks_id_seq; Type: SEQUENCE SET; Schema: supabase_functions; Owner: supabase_functions_admin
--

SELECT pg_catalog.setval('"supabase_functions"."hooks_id_seq"', 1, false);


--
-- PostgreSQL database dump complete
--

RESET ALL;
