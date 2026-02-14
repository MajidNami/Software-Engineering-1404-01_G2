# Architecture Overview (MVC)

Django naturally follows an MVC-like separation:

- **Models**: `crm/models/*` map 1:1 to MySQL tables such as `cmr_comments`, `cmr_ratings`, `cmr_media`, `cmr_reports` fileciteturn1file5L31-L52 fileciteturn1file1L19-L40
- **Controllers**: `crm/controllers/*`
  - `crm/controllers/api.py` exposes the required service list endpoints fileciteturn1file12L4-L23
  - `crm/controllers/ui.py` renders the 2 UIs described (user interaction + management) fileciteturn1file14L10-L16
- **Views (Templates)**: `crm/templates/crm/*` render the functional UI; JS uses `fetch()` to call APIs for real-time interaction.

Business logic is kept out of controllers:
- **Domain services**: `crm/services/*` encapsulate rules like:
  - `PostComment` sets comment status to `pending` and validates reply depth fileciteturn1file12L21-L23
  - `postRate` updates `cmr_rating_aggregates` and updates existing rating if present fileciteturn1file9L4-L7
  - `Report` inserts pending report and increments `report_count`, with threshold-based moderation fileciteturn1file12L30-L32 fileciteturn1file11L14-L16
  - `updateReportStatus(valid)` rejects the related comment/media fileciteturn1file7L33-L35

