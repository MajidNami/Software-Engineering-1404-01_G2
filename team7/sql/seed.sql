SET NAMES utf8mb4;

-- Users
INSERT INTO cmr_users (id_user, username, email, is_moderator) VALUES
('11111111-1111-1111-1111-111111111111','alice','alice@example.com', FALSE),
('22222222-2222-2222-2222-222222222222','bob','bob@example.com', FALSE),
('99999999-9999-9999-9999-999999999999','mod','mod@example.com', TRUE)
ON DUPLICATE KEY UPDATE username=VALUES(username), email=VALUES(email), is_moderator=VALUES(is_moderator);

-- Targets (Tourism/Touring Place entity)
INSERT INTO cmr_targets (id_target, entity_type, entity_id, target_name) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','tourism_place','aaaaaaaa-0000-0000-0000-000000000000','Niagara-ish Waterfall'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb','tourism_place','bbbbbbbb-0000-0000-0000-000000000000','Historic Bazaar')
ON DUPLICATE KEY UPDATE target_name=VALUES(target_name);
