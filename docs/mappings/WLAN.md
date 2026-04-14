# WLAN Field Mapping: Central ↔ Mist

Fields marked **[MAPPED]** have a direct or translatable equivalent.
Fields marked **[UNMAPPED]** exist on only one platform.
Fields marked **[NEEDS REVIEW]** may have a mapping but need confirmation.

---

## Naming / Identity

Central and Mist have fundamentally different naming models:

- **Central**: WLAN profile name ≠ SSID name. The profile has a name (e.g. "ADAMS-WIFI2")
  and an optional SSID alias (e.g. "AdamsLAB") that resolves to the broadcasted SSID name
  (e.g. "ADAMS-WIFI"). When `essid.use-alias` is true, the alias must be resolved via
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

| Central | Mist | Status |
|---------|------|--------|
| personal-security.wpa-passphrase | auth.psk | **[MAPPED]** direct for simple PSK |
| personal-security.mpsk-cloud-auth | dynamic_psk.enabled + dynamic_psk.source="cloud" | **[MAPPED]** translate |
| personal-security.mpsk-local-profile | dynamic_psk.enabled + dynamic_psk.source="local" | **[NEEDS REVIEW]** |
| personal-security.wpa-passphrase-alias | (none) | **[UNMAPPED]** Central uses aliases |
| (none) | dynamic_psk.default_psk | **[UNMAPPED]** Mist only |
| (none) | dynamic_psk.default_vlan_id | **[UNMAPPED]** Mist only |

### RADIUS / Server Groups

Central uses named server groups. Mist uses inline server definitions.
Resolution workflow:

**Central → Mist:**
1. Get `auth-server-group` name from WLAN profile (e.g. "NAC-RADIUS")
2. Call `central_get_server_groups(name="NAC-RADIUS")` to resolve to actual servers
3. Map each server in the group to a Mist `auth_servers` entry (host, port, secret)
4. Same for `acct-server-group` → `acct_servers`

**Mist → Central:**
1. Get individual servers from `auth_servers` array
2. Check if a matching server group already exists in Central
3. If not, the sync should note that a server group needs to be created manually
   (or create one if write tools support it)

| Central | Mist | Status |
|---------|------|--------|
| auth-server-group ("NAC-RADIUS") | auth_servers [{host, port, secret}] | **[MAPPED]** requires server group resolution |
| acct-server-group ("NAC-RADIUS") | acct_servers [{host, port, secret}] | **[MAPPED]** requires server group resolution |
| primary-auth-server (when no group) | auth_servers[0].host | **[MAPPED]** direct |
| backup-auth-server (when no group) | auth_servers[1].host | **[MAPPED]** direct |
| primary-acct-server (when no group) | acct_servers[0].host | **[MAPPED]** direct |
| backup-acct-server (when no group) | acct_servers[1].host | **[MAPPED]** direct |
| radius-accounting (bool) | (presence of acct_servers) | **[MAPPED]** translate |
| radius-interim-accounting-interval | acct_interim_interval | **[MAPPED]** direct |
| radius-reauth-interval | (none) | **[UNMAPPED]** Central only |
| cloud-auth | (none) | **[UNMAPPED]** Central only |
| (none) | auth_servers_nas_id | **[UNMAPPED]** Mist only |
| (none) | auth_servers_nas_ip | **[UNMAPPED]** Mist only |
| (none) | auth_servers_retries | **[UNMAPPED]** Mist only |
| (none) | auth_servers_timeout | **[UNMAPPED]** Mist only |
| (none) | auth_server_selection | **[UNMAPPED]** Mist only |
| (none) | coa_servers | **[UNMAPPED]** Mist only (not supported with MPSK RADIUS) |
| (none) | radsec | **[UNMAPPED]** Mist only |

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

## Radio Capabilities (Central only — Mist manages via RF template)

| Central | Mist | Status |
|---------|------|--------|
| high-throughput (all fields) | (none) | **[UNMAPPED]** |
| high-efficiency (all fields) | (none) | **[UNMAPPED]** |
| extremely-high-throughput (all fields) | (none) | **[UNMAPPED]** |
| g-legacy-rates (all fields) | (none) | **[UNMAPPED]** |
| a-legacy-rates (all fields) | (none) | **[UNMAPPED]** |

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
| **MAPPED** (direct or translatable) | ~30 |
| **NEEDS REVIEW** | ~6 |
| **UNMAPPED** Central-only | ~80+ |
| **UNMAPPED** Mist-only | ~30+ |

The MAPPED fields cover the essential settings for a functional WLAN sync:
SSID identity (with alias resolution), enabled state, auth mode, PSK/MPSK,
RADIUS (when not using server groups), VLAN, RF band, DTIM, max clients,
idle timeout, fast roaming, client isolation, WMM, ARP filter, and
broadcast control.

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
