"""Mist guided prompts for site provisioning workflows."""


def register(mcp):

    @mcp.prompt
    def provision_site_from_template(
        source_site_name: str,
        target_site_name: str,
        target_address: str,
    ) -> str:
        """Provision a new Mist site cloned from an existing site using templates."""
        return f"""
Provision a new site "{target_site_name}" at "{target_address}" based \
on the configuration of "{source_site_name}":

1. Call `mist_get_self(action_type=account_info)` to get the org_id.
2. Call `mist_get_configuration_objects(org_id=<org_id>, \
object_type=org_sites, name="{source_site_name}")` to get the source \
site config. Note the rftemplate_id, sitetemplate_id, \
networktemplate_id, gatewaytemplate_id, secpolicy_id, \
alarmtemplate_id, and sitegroup_ids.
3. Call `mist_get_configuration_objects(org_id=<org_id>, \
object_type=site_wlans, site_id=<source_site_id>, computed=true)` to \
get all WLANs at the source site.
4. For each WLAN returned: check if it has a `template_id` field. \
If yes, it comes from an org-level WLAN template (good — no action \
needed). If no `template_id`, it is a site-level WLAN that should be \
migrated to an org-level template.
5. For any site-level WLANs found: check \
`mist_get_configuration_objects(org_id=<org_id>, \
object_type=org_wlantemplates)` for an existing template containing \
a WLAN with the same SSID. If none exists, create a new org-level \
WLAN template using `mist_change_org_configuration_objects(\
action_type=create, object_type=wlantemplates, payload=...)` and \
then create the WLAN inside it with object_type=wlans and the \
template_id of the new template. Assign the template to the same \
site groups as the source site.
6. Create the new site: `mist_change_org_configuration_objects(\
action_type=create, object_type=sites, payload={{name: \
"{target_site_name}", address: "{target_address}", \
rftemplate_id: <from_source>, sitetemplate_id: <from_source>, \
networktemplate_id: <from_source>, timezone: <from_source>, \
country_code: <from_source>}})`.
7. Add the new site to the same site groups as the source site. For \
each sitegroup_id: call `mist_get_configuration_objects(org_id=\
<org_id>, object_type=org_sitegroups, object_id=<sitegroup_id>)`, \
add the new site_id to the site_ids list, then call \
`mist_change_org_configuration_objects(action_type=update, \
object_type=sitegroups, object_id=<sitegroup_id>, \
payload=<updated_sitegroup>)`.
8. Do NOT create any site-level WLANs on the new site. Templates \
assigned via site groups will deliver all SSIDs automatically.
9. Report: site created, site groups assigned, templates applied, \
and whether any site-level WLANs from the source were migrated to \
org-level templates.
        """.strip()

    @mcp.prompt
    def bulk_provision_sites(
        source_site_name: str,
        site_list_description: str,
    ) -> str:
        """Provision multiple sites cloned from an existing site using templates."""
        return f"""
Bulk provision sites based on "{source_site_name}" configuration. \
Sites to create: {site_list_description}

PHASE 1 — Analyze source (do this ONCE):
1. Call `mist_get_self(action_type=account_info)` to get the org_id.
2. Call `mist_get_configuration_objects(org_id=<org_id>, \
object_type=org_sites, name="{source_site_name}")` to get the source \
site config. Note rftemplate_id, sitetemplate_id, \
networktemplate_id, gatewaytemplate_id, secpolicy_id, \
alarmtemplate_id, and sitegroup_ids.
3. Call `mist_get_configuration_objects(org_id=<org_id>, \
object_type=site_wlans, site_id=<source_site_id>, computed=true)` to \
get all WLANs. Identify which are template-based (have template_id) \
vs site-level (no template_id).
4. For any site-level WLANs: check if an equivalent org-level WLAN \
template already exists (match by SSID). If not, create one using \
`mist_change_org_configuration_objects` with object_type=\
wlantemplates and then object_type=wlans. Assign the template to \
the source site's site groups. This step ensures all SSIDs are \
template-based before cloning.

PHASE 2 — Create each site (loop):
For each site in the list:
5. Create the site: `mist_change_org_configuration_objects(\
action_type=create, object_type=sites, payload={{name: <site_name>, \
address: <site_address>, rftemplate_id: <from_source>, \
sitetemplate_id: <from_source>, networktemplate_id: <from_source>, \
timezone: <from_source>, country_code: <from_source>}})`.
6. Add the new site to the same site groups as the source. Update \
each site group's site_ids list to include the new site_id.
7. Do NOT create any site-level WLANs. Templates applied via site \
groups deliver all SSIDs automatically.

PHASE 3 — Report:
8. Present a summary table with columns: Site Name, Status \
(Created/Failed), Site Groups Assigned, Templates Applied.
9. Note any site-level WLANs from the source that were migrated to \
org-level templates in Phase 1.
10. Confirm: "All SSIDs are delivered via org-level WLAN templates \
assigned through site groups. No site-level WLANs were created."
        """.strip()
