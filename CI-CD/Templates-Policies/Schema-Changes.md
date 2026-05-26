# Schema Changes
These are base concepts and building blocks for a schema change policy for a team.
1. Submit a proposed change by including (IN A TICKET!)
	- change type => VALUE CHANGE, RENAME, NEW COLUMN, REMOVE COLUMN, NEW TABLE, REMOVE TABLE
	- reason for change
	- benefits of change
2. Discuss Changes in a weekly meeting.
3. If approved for implementation change in the excel schema by 
	- NEW COLUMN => add the column + change column name to orange
	- VALUE CHNAGE => change column name to blue
	- REMOVE => change column name to red , until actually deleted from production.
4. Create and link a sub-ticket for each team approving they have implemented the code for the schema change.
5. Write code to represent deploying the change
6. Test in the DEV + UAT
7. Once all approved and test are past. Deploy 

Excel Info Rules
1. Document which columns a specific team/IAM User alters
	Green -> Insert Only
	Orange -> Insert + Updates
	Black -> Inserts + Updates + Delete
	Red -> Delete
2. For “Schema Change Log”
	- Add any approved changes to this log.
	- Leave status as APPROVED, IN-DEV, TESTING, READY FOR PROD, DEPLOYED.

==============================
CHECKLIST OF CHANGES
==============================

1. Change SQL Create Table
2. Change Upsert Procedure
3. Change the SQL Alchemy Model
4. Change the Pydantic Model
5. Change the Software APP Prisma
6. Create deployment code

Secondary Effects:
1. Change import BI Queries and QC’s
2. If column rename adjust python code

---
# Ticket Template
---
Title FormatT1 - [CHANGE TYPE] | [table_name].[column_name] | Short description Examples: T1 - NEW COLUMN | claim_output_file_log.reviewed_by_id | Track reviewer per log entry T1 - RENAME | claim_contention.ace_denial_reason → ace_denial_reasons | Support multiple reasons T1 - NEW TABLE | form_stage_history | Track stage transitions per form uncomment this out when creating .md file:    /label ~"Schema-Change"


/label ~"Software-Request"


<!-- ⚠️⚠️⚠️⚠️⚠️⚠️ REQUIRED ⚠️⚠️⚠️⚠️⚠️⚠️ -->
<!-- link the originating ticket from the claims repo -->
<!-- e.g. claims#1234 -->
/relate claims#

Change Request OverviewChange Type: Select one: VALUE CHANGE | RENAME | NEW COLUMN | REMOVE COLUMN | NEW TABLE | REMOVE TABLEReason for Change: Benefits of Change: Schema SpecificationFill out only the section(s) that apply to your change type. Remove any sections that are not relevant (e.g. no index changes? delete that section entirely). Table  Table Name  Schema / Database  Column ChangesColumn Name Action Data Type Nullable Default Notes column_name ADD / REMOVE / RENAME / MODIFY VARCHAR(255) YES / NO NULL        RENAME — fill in both old and new name in the Notes column (e.g. old_name → new_name) Index ChangesIndex Name Action Columns Unique Notes idx_name ADD / REMOVE col1, col2 YES / NO       New Table Definition (if applicable)   CREATE TABLE table_name (
    id          INT             NOT NULL,
    -- add columns here
);Checklist of ChangesComplete all items that apply. Cross out any that are not applicable. Primary ChangesUpdate SQL Create Table Update Upsert Procedure Update SQLAlchemy Model Update Pydantic Model Update Software App Prisma schema + migration Write deployment code Secondary / Downstream EffectsUpdate import BI Queries and QCs Update Python code if column is renamed Excel Schema TrackingAfter approval, update the shared Excel schema doc: MDC-Data-Dictionary-Official.xlsx NEW COLUMN → Add column, set column name to {\color{orange}{\textbf{ORANGE}}} VALUE CHANGE → Set column name to {\color{blue}{\textbf{BLUE}}} REMOVE → Set column name to {\color{red}{\textbf{RED}}} (until deleted from production) Add entry to the Schema Change Log tab with status: APPROVED Schema Change Log Status: APPROVED → IN-DEV → TESTING → READY FOR PROD → DEPLOYED Sub-Tickets (Team Sign-offs)Create a linked sub-ticket for each team confirming they have implemented their side of the change. Sub-ticket: Team nameSub-ticket: Team nameSub-ticket: Team nameTesting & DeploymentTested in DEV Tested in STAGING All team sub-tickets approved Ready to deploy to Production Notes / Additional ContextWeekly meeting date this was discussed + approved, links to related tickets, migration notes, etc.
