# WLAN Field Mapping: Central ↔ Mist

Fields marked **[MAPPED]** have a direct or translatable equivalent.
Fields marked **[UNMAPPED]** exist on only one platform.
Fields marked **[NEEDS REVIEW]** may have a mapping but need confirmation.

---

## Naming / Identity

Central and Mist have fundamentally different naming models:

- **Central**: WLAN profile name ≠ SSID name. The profile has a name (e.g. "CORP-WIFI-2")
  and an optional SSID alias (e.g. "CORP-LAB") that resolves to the broadcasted SSID name
  (e.g. "CORP-WIFI"). When `essid.use-alias` is true, the alias must be resolved via
  `GET /network-config/v1alpha1/aliases/{alias_name}` to get the actual SSID.
- **Mist**: WLAN template name is the container. The WLAN `ssid` field IS the broadcasted name.

### Sync Mapping

| Direction | Central | Mist |
|-----------|---------|------|
| Central → Mist | Profile name → WLAN template name | Resolved SSID (from alias or essid.name) → WLAN `ssid` |
| Mist → Central | WLAN template name → Profile name | WLAN `ssid` → essid.name (or create alias) |

| Central | Mist | Status |
|---------|------|--------|
| profile name (ssid field) | WLAN template name | **[MAPPED]** naming convention |
| essid.alias (resolved) | ssid | **[MAPPED]** requires alias lookup |
| essid.name | ssid (when no alias) | **[MAPPED]** direct |
| essid.use-alias | (no equivalent) | **[UNMAPPED]** Central only |
| description | (none) | **[UNMAPPED]** Central only |

---

## Core SSID Settings

| Central | Mist | Status |
|---------|------|--------|
| enable | enabled | **[MAPPED]** direct |
| hide-ssid | hide_ssid | **[MAPPED]** direct |
| rf-band ("BAND_ALL", "24GHZ_5GHZ", "5GHZ", etc) | bands (["24","5","6"]) + interface | **[MAPPED]** translate enum→array |
| forward-mode ("FORWARD_MODE_BRIDGE") | (bridge is default) | **[MAPPED]** skip if tunneled |
| type ("EMPLOYEE", "GUEST", etc) | (none) | **[UNMAPPED]** Central only |

---

## VLAN

Central uses named VLANs. Mist uses VLAN IDs. Resolution workflow:

**Central → Mist:**
1. Get `vlan-name` from WLAN profile (e.g. "USER-VLAN")
2. Call `central_get_named_vlans(name="USER-VLAN")` to get the named VLAN config
3. If the named VLAN has a VLAN ID directly → use that ID
4. If the named VLAN uses an alias → call `central_get_aliases(alias_name=...)` to resolve
5. In Mist: set `vlan_enabled=true`, `dynamic_vlan.enabled=true`,
   `dynamic_vlan.type="airespace-interface-name"`, use the resolved VLAN ID as
   `dynamic_vlan.default_vlan_ids`, and the named VLAN name as the key

**Mist → Central:**
1. If Mist has `dynamic_vlan.enabled=true` with entries, use the first entry only
2. The VLAN name becomes the Central `vlan-name`
3. The VLAN ID becomes the Central named VLAN's ID (may need to create the named VLAN)

| Central | Mist | Status |
|---------|------|--------|
| vlan-selector ("NAMED_VLAN") | vlan_enabled (bool) | **[MAPPED]** translate |
| vlan-name ("USER-VLAN") | dynamic_vlan.vlans (first entry name) | **[MAPPED]** requires named VLAN lookup |
| (resolved VLAN ID) | dynamic_vlan.default_vlan_ids[0] | **[MAPPED]** requires named VLAN lookup |
| vlan-id-range | (none) | **[UNMAPPED]** Central only |
| (none) | vlan_pooling | **[UNMAPPED]** Mist only |
| (none) | vlan_ids (array) | **[UNMAPPED]** Mist only |

---

## Security / Auth

### Auth Mode

| Central | Mist | Status |
|---------|------|--------|
| opmode "OPEN" | auth.type "open" | **[MAPPED]** |
| opmode "WPA2_PERSONAL" | auth.type "psk" | **[MAPPED]** |
| opmode "WPA3_PERSONAL" | auth.type "psk" + auth.pairwise ["wpa3"] | **[MAPPED]** translate |
| opmode "WPA2_ENTERPRISE" | auth.type "eap" + auth.pairwise ["wpa2-ccmp"] | **[MAPPED]** translate |
| opmode "WPA3_ENTERPRISE_CCM_128" | auth.type "eap" + auth.pairwise ["wpa3","wpa2-ccmp"] | **[MAPPED]** translate |
| opmode "WPA2_MPSK_AES" | auth.type "psk" + dynamic_psk.enabled=true | **[MAPPED]** translate |
| wpa3-transition-mode-enable | auth.pairwise includes both wpa3 and wpa2 | **[MAPPED]** translate |

### PSK / MPSK

When Central uses `wpa-passphrase-alias`, resolve via
`central_get_aliases(alias_name=<alias>)` to get the actual PSK value
before mapping to Mist `auth.psk`. Like RADIUS aliases, PSK aliases
can be scoped per-site for different passphrases at different locations.

| Central | Mist | Status |
|---------|------|--------|
| personal-security.wpa-passphrase | auth.psk | **[MAPPED]** direct for simple PSK |
| personal-security.wpa-passphrase-alias | auth.psk (resolved via alias lookup) | **[MAPPED]** resolve alias to get PSK value |
| personal-security.mpsk-cloud-auth | dynamic_psk.enabled + dynamic_psk.source="cloud" | **[MAPPED]** translate |
| personal-security.mpsk-local-profile | dynamic_psk (local) | **[DEFERRED]** complex: Central MPSK local uses a profile with PSKs tied to Aruba user roles (role→VLAN). Mapping would require creating a role + VLAN + PSK entry. Deferred to future release. |
| (Central default VLAN via role) | dynamic_psk.default_vlan_id | **[DEFERRED]** part of MPSK local mapping |
| (none) | dynamic_psk.default_psk | **[UNMAPPED]** Mist only (no equivalent in Central MPSK local) |

### RADIUS / Server Groups

Central uses named server groups with aliases for server IPs.
Mist uses inline server definitions with template variables for server IPs.
Both platforms use indirection to allow the same WLAN profile to resolve
to different RADIUS servers per site.

#### Central Alias Resolution

Central server groups reference servers by FQDN, IP address, or by
**alias**. Aliases are named references that resolve to actual values
(e.g. an alias `radius_primary` → `10.1.1.100` or `radius.corp.local`).
Aliases can be scoped at different levels in the hierarchy (Global, Site
Collection, Site) so the same WLAN profile resolves to different RADIUS
servers per site.

**Resolution steps:**
1. Get `auth-server-group` name from WLAN profile (e.g. "NAC-RADIUS")
2. Call `central_get_server_groups(name="NAC-RADIUS")` to get the server list
3. For each server in the group, check if the host uses an alias
4. If aliased: call `central_get_aliases(alias_name=<alias>)` to resolve
   the alias to the actual FQDN or IP address
5. Note: aliases may have per-site overrides. The effective value depends
   on the scope where the WLAN is applied (Global → Site Collection → Site)

#### Mist Template Variable Resolution

Mist WLANs use **template variables** in server `host` fields (e.g.
`{{auth_srv1}}`). Variables are resolved from site settings (`vars` dict)
at runtime. This allows a single org-level WLAN template to point to
different RADIUS servers (FQDN or IP) at each site.

**Resolution steps:**
1. Get `auth_servers` from the WLAN — each entry has a `host` field
2. If `host` matches `{{variable_name}}` pattern → it's a template variable
3. Call `mist_get_org_or_site_info(org_id=<org_id>, site_id=<site_id>,
   info_type=setting)` to get site settings including `vars`
4. Look up the variable name in `vars` to get the actual FQDN or IP address
5. Variables inherit: org `vars` → sitegroup `vars` → site `vars`
   (closest scope wins, like Central aliases)

#### Sync Workflow

**Central → Mist:**
1. Get `auth-server-group` name from WLAN profile (e.g. "NAC-RADIUS")
2. Call `central_get_server_groups(name="NAC-RADIUS")` to resolve to servers
3. For each server, resolve any aliases via `central_get_aliases`
4. In Mist: use template variables (`{{auth_srv1}}`, `{{auth_srv2}}`) in
   `auth_servers[].host` — do NOT hardcode IPs in the WLAN definition
5. Define the resolved addresses in each Mist site's `vars` dict:
   `{"auth_srv1": "10.1.1.100", "auth_srv2": "radius2.corp.local"}`
6. Same pattern for `acct-server-group` → `acct_servers` with variables
   like `{{acct_srv1}}`
7. Map port, secret, and other server attributes directly

**Mist → Central:**
1. Get `auth_servers` from the Mist WLAN
2. If hosts use template variables → resolve from site settings `vars`
3. Check if a matching server group already exists in Central
4. If not, the sync should note that a server group needs to be created
   manually (or create one if write tools support it)
5. For per-site variation: create Central aliases matching the variable
   names and set per-scope values to match each site's `vars`

| Central | Mist | Status |
|---------|------|--------|
| auth-server-group ("NAC-RADIUS") | auth_servers [{host, port, secret}] | **[MAPPED]** requires server group resolution |
| acct-server-group ("NAC-RADIUS") | acct_servers [{host, port, secret}] | **[MAPPED]** requires server group resolution |
| primary-auth-server (when no group) | auth_servers[0].host | **[MAPPED]** direct |
| backup-auth-server (when no group) | auth_servers[1].host | **[MAPPED]** direct |
| primary/backup server ordering | auth_server_selection ("ordered") | **[MAPPED]** Central primary/backup = Mist ordered selection |
| primary-acct-server (when no group) | acct_servers[0].host | **[MAPPED]** direct |
| backup-acct-server (when no group) | acct_servers[1].host | **[MAPPED]** direct |
| radius-accounting (bool) | (presence of acct_servers) | **[MAPPED]** translate |
| radius-interim-accounting-interval | acct_interim_interval | **[MAPPED]** direct |
| nas-identifier (in server config) | auth_servers_nas_id | **[MAPPED]** different location (server vs WLAN) |
| nas-ip-address (in server config) | auth_servers_nas_ip | **[MAPPED]** different location (server vs WLAN) |
| dynamic-authorization-enable (in server) | coa_servers (list) | **[MAPPED]** Central enables per-server, Mist defines separate CoA entries |
| enable-radsec (in server config) | radsec.enabled | **[MAPPED]** both support RadSec |
| radius-reauth-interval | (none) | **[UNMAPPED]** Central only |
| cloud-auth | (none) | **[UNMAPPED]** Central only |
| (none) | auth_servers_retries | **[UNMAPPED]** Mist only |
| (none) | auth_servers_timeout | **[UNMAPPED]** Mist only |

### MAC Auth

| Central | Mist | Status |
|---------|------|--------|
| mac-authentication (bool) | auth.enable_mac_auth (bool) | **[MAPPED]** direct |
| mac-authentication-delimiter | (none) | **[UNMAPPED]** Central only |
| mac-authentication-upper-case | (none) | **[UNMAPPED]** Central only |
| l2-auth-failthrough | (none) | **[UNMAPPED]** Central only |
| dot1x-timer-idrequest-period | (none) | **[UNMAPPED]** Central only |

### Dynamic VLAN

| Central | Mist | Status |
|---------|------|--------|
| (role-based, via roles not WLAN profile) | dynamic_vlan.enabled | **[UNMAPPED]** different architecture |
| (none) | dynamic_vlan.vlans (role→VLAN map) | **[UNMAPPED]** Mist only |
| (none) | dynamic_vlan.default_vlan_ids | **[UNMAPPED]** Mist only |
| (none) | dynamic_vlan.type | **[UNMAPPED]** Mist only |

---

## Performance / Radio

| Central | Mist | Status |
|---------|------|--------|
| dtim-period | dtim | **[MAPPED]** direct |
| max-clients-threshold | max_num_clients | **[MAPPED]** direct (0=unlimited in Mist) |
| inactivity-timeout | max_idletime | **[MAPPED]** direct (both in seconds) |
| dot11r (bool) | roam_mode ("NONE", "OKC", "11r") | **[MAPPED]** translate |
| dot11k (bool) | (none) | **[UNMAPPED]** Central only |
| dot11v (bool) | (none) | **[UNMAPPED]** Central only |
| mobility-domain-id | (none) | **[UNMAPPED]** Central only |
| dot11r-key-duration | (none) | **[UNMAPPED]** Central only |
| dot11r-ondemand-keyfetch | (none) | **[UNMAPPED]** Central only |
| mfp-capable | (none) | **[UNMAPPED]** Central only |
| mfp-required | (none) | **[UNMAPPED]** Central only |
| opp-key-caching | (NOT enable_local_keycaching) | **[UNMAPPED]** different features |
| explicit-ageout-client | (none) | **[UNMAPPED]** Central only |
| short-preamble | (none) | **[UNMAPPED]** Central only |
| rts-threshold | (none) | **[UNMAPPED]** Central only |
| max-retries | (none) | **[UNMAPPED]** Central only |
| mbo | (none) | **[UNMAPPED]** Central only |
| qbss-load | (none) | **[UNMAPPED]** Central only |
| ftm-responder | (none) | **[UNMAPPED]** Central only |
| auth-req-thresh | (none) | **[UNMAPPED]** Central only |
| local-probe-req-thresh | (none) | **[UNMAPPED]** Central only |
| (none) | band_steer | **[UNMAPPED]** Mist only (Central uses RF template) |
| (none) | band_steer_force_band5 | **[UNMAPPED]** Mist only |
| (none) | limit_probe_response | **[UNMAPPED]** Mist only |
| (none) | disable_11ax | **[UNMAPPED]** Mist only |
| (none) | disable_11be | **[UNMAPPED]** Mist only |
| (none) | disable_ht_vht_rates | **[UNMAPPED]** Mist only |
| (none) | hostname_ie | **[UNMAPPED]** Mist only |
| (none) | legacy_overds | **[UNMAPPED]** Mist only |
| (none) | roam_mode ("OKC") | **[UNMAPPED]** Mist only (Central has opp-key-caching separately) |
| (none) | rateset (per-band rate templates) | **[UNMAPPED]** Mist only |

---

## Client Isolation / Broadcast

| Central | Mist | Status |
|---------|------|--------|
| client-isolation (bool) | isolation (bool) | **[MAPPED]** direct |
| deny-inter-user-bridging | limit_bcast (bool) | **[MAPPED]** translate |
| broadcast-filter-ipv4 ("BCAST_FILTER_ARP") | arp_filter (bool) | **[MAPPED]** translate enum→bool |
| broadcast-filter-ipv6 | (none) | **[UNMAPPED]** Central only |
| local-proxy-ns | (none) | **[UNMAPPED]** Central only |
| deny-local-routing | (none) | **[UNMAPPED]** Central only |
| (none) | l2_isolation | **[UNMAPPED]** Mist only |
| (none) | enable_wireless_bridging | **[UNMAPPED]** Mist only |
| (none) | allow_mdns | **[UNMAPPED]** Mist only |
| (none) | allow_ssdp | **[UNMAPPED]** Mist only |
| (none) | allow_ipv6_ndp | **[UNMAPPED]** Mist only |

---

## WMM / QoS

| Central | Mist | Status |
|---------|------|--------|
| wmm-cfg.uapsd | disable_uapsd (inverted bool) | **[MAPPED]** inverted |
| wmm-cfg.video-dscp | (none) | **[UNMAPPED]** Central only |
| wmm-cfg.voice-dscp | (none) | **[UNMAPPED]** Central only |
| wmm-cfg (detailed per-AC settings) | disable_wmm (bool) | **[MAPPED]** simplified |
| (none) | qos.class | **[UNMAPPED]** Mist only |
| (none) | app_qos | **[UNMAPPED]** Mist only |

---

## Bonjour / mDNS

| Central | Mist | Status |
|---------|------|--------|
| (not in WLAN profile) | bonjour.enabled | **[UNMAPPED]** Mist only (Central may handle elsewhere) |
| (none) | bonjour.services (per-service scope) | **[UNMAPPED]** Mist only |
| (none) | bonjour.additional_vlan_ids | **[UNMAPPED]** Mist only |

---

## Data Rates / Radio Capabilities

Central bundles data rates with other settings into network config profiles.
Mist separates data rates (`rateset`) from other features (arp_filter, roam_mode, etc.).

### Data Rate Profile Mapping

| Central Profile | Central MBR | Mist rateset template | Notes |
|----------------|-------------|----------------------|-------|
| Most Compatible | 1-2 Mbps | `compatible` | Both enable all rates |
| Balanced | 12 Mbps | `no-legacy` | Both disable legacy 802.11b |
| High Density | 24 Mbps | `high-density` | Both set 24 Mbps MBR |
| Custom | varies | closest match | Map to nearest profile based on MBR. Never use custom in Mist unless user explicitly requests it. |

**MBR-based mapping logic for custom Central rates:**
- MBR ≤ 2 Mbps → Mist `compatible`
- MBR 6-12 Mbps → Mist `no-legacy`
- MBR ≥ 24 Mbps → Mist `high-density`

**Note:** Central's profiles also set broadcast filter, 11r, 11k, OKC/PMK.
These are mapped separately in Mist (arp_filter, roam_mode, dot11k is Central-only).

| Central | Mist | Status |
|---------|------|--------|
| g-legacy-rates.basic-rates | rateset.24.template | **[MAPPED]** translate to profile name |
| a-legacy-rates.basic-rates | rateset.5.template | **[MAPPED]** translate to profile name |
| (none) | rateset.6.template | **[UNMAPPED]** Mist only (6 GHz rates) |
| high-throughput (HT/VHT settings) | (none) | **[UNMAPPED]** Central only (Mist auto-negotiates) |
| high-efficiency (HE settings) | (none) | **[UNMAPPED]** Central only |
| extremely-high-throughput (EHT) | disable_11be (inverted) | **[MAPPED]** EHT enable=true → disable_11be=false |

---

## Role-Based / NAC (Central only)

| Central | Mist | Status |
|---------|------|--------|
| assignment-rules | (none) | **[UNMAPPED]** |
| pre-auth-role | (none) | **[UNMAPPED]** |
| mac-auth-only-role | (none) | **[UNMAPPED]** |
| machine-auth | (none) | **[UNMAPPED]** |
| default-role | (none) | **[UNMAPPED]** |
| download-role | (none) | **[UNMAPPED]** |

---

## Captive Portal

| Central | Mist | Status |
|---------|------|--------|
| captive-portal-type | portal.enabled + portal.auth | **[NEEDS REVIEW]** very different models |
| captive-portal | portal.external_portal_url | **[NEEDS REVIEW]** |
| captive-portal-landing-page-delay | (none) | **[UNMAPPED]** Central only |
| captive-portal-proxy-server | (none) | **[UNMAPPED]** Central only |
| (none) | portal_allowed_hostnames | **[UNMAPPED]** Mist only |
| (none) | portal_allowed_subnets | **[UNMAPPED]** Mist only |
| (none) | portal_denied_hostnames | **[UNMAPPED]** Mist only |
| (none) | portal_api_secret | **[UNMAPPED]** Mist only |
| (none) | portal (SSO, social login, sponsor) | **[UNMAPPED]** Mist only |

---

## Miscellaneous (Central only)

advertise-location, advertise-apname, advertise-timing,
advertise-location-identifier, advertise-location-civic,
passpoint, hotspot-profile, zone, mbssid-group-profile,
time-range, out-of-service, auth-survivability, airpass,
wispr, denylist, denylist-sco-attack, pan, termination,
enforce-dhcp, content-filtering, work-without-uplink,
bandwidth-limit, cluster-preemption, ssid-utf8, cdc,
disable-on-6ghz-mesh, auth-failure-code, refresh-direction,
rrm-quiet-ie, optimize-mcast-rate, dmo, pmk-cache-delete-on-leave,
server-load-balancing, radius-loc-obj-in-access,
radius-loc-obj-in-accting, radius-ip-based-acct-session,
max-authentication-failures, priority-use-local-cache,
external-server, max-ipv4-users, called-station-id,
internal-auth-server, exclude-uplink, use-ip-for-calling-station-id,
cp-accounting-mode, qos-management, allowed-5ghz-radio,
allowed-6ghz-radio

## Miscellaneous (Mist only)

sle_excluded, reconnect_clients_when_roaming_mxcluster,
block_blacklist_clients, client_limit_down/up_enabled,
wlan_limit_down/up_enabled, no_static_dns, no_static_ip,
acct_immediate_update, disable_v1/v2_roam_notify,
disable_when_gateway_unreachable, disable_when_mxtunnel_down,
cisco_cwa, airwatch, dns_server_rewrite, schedule,
mist_nac, hotspot20, app_limit

---

## Summary

| Category | Count |
|----------|-------|
| **MAPPED** (direct or translatable) | ~38 |
| **DEFERRED** (complex, future release) | ~2 (MPSK local) |
| **UNMAPPED** Central-only | ~75+ |
| **UNMAPPED** Mist-only | ~25+ |

The MAPPED fields cover the essential settings for a functional WLAN sync:
SSID identity (with alias resolution), enabled state, auth mode, PSK
(including alias resolution), MPSK cloud, RADIUS (with server group
resolution, NAS ID/IP, CoA, RadSec), VLAN (with named VLAN resolution),
RF band, DTIM, max clients, idle timeout, fast roaming, client isolation,
WMM, ARP filter, and broadcast control.

DEFERRED: MPSK local mapping requires creating Aruba user roles with VLAN
assignments — complex and deferred to a future release.

UNMAPPED fields are platform-specific and preserved on their native
platform during sync. They are not modified or deleted.

### Resolved Questions

1. **RADIUS server groups** — Resolved via `central_get_server_groups` tool
   (`GET /network-config/v1alpha1/server-groups/{name}`)
2. **VLAN name→ID** — Resolved via `central_get_named_vlans` tool
   (`GET /network-config/v1alpha1/named-vlan/{name}`). If the named VLAN
   uses an alias, resolve via `central_get_aliases`.
3. **Captive portal** — Deferred to a future release. Portal SSIDs will be
   synced with a note that portal configuration requires manual setup.
