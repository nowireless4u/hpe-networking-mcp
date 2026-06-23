"""Canonical (platform-neutral) WLAN model — the translation-engine pivot.

Every platform WLAN **reader** produces a ``CanonicalWlan``; every platform
**writer** consumes one. So ``source → target`` is always
``writer_target(reader_source(data))`` and the platform-specific construction
logic (Central profile-name/alias, opmode enum, RADIUS, assignment scope, …)
lives **once** per platform, shared across all sources — no N² pairwise mappers.

The field set is validated against ``docs/mappings/WLAN.md`` (the authoritative
Mist↔Central field map). Notable structural decisions, agreed with the
maintainer:

- **NAC is its own canonical + writer.** An enterprise WLAN here only *references*
  an auth source (``security.auth_source``); creating the Central NAC / server
  group is a separate translation this WLAN depends on.
- **Cloud MPSK is its own solution.** This model only flags ``mode=mpsk`` +
  ``mpsk.source=cloud``; the Central writer sets the opmode + cloud-auth but
  never copies key values (Central rejects manually-set MPSK). Local MPSK is
  deferred (WLAN.md).
- **Unmapped, platform-only fields are preserved** by the writer on update
  (merge/PATCH), never clobbered — so this model intentionally does NOT carry
  every native field, only the translatable set.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class KeyMgmt(StrEnum):
    """Platform-neutral key-management / auth method (one axis of the opmode triplet)."""

    OPEN = "open"  # no auth
    OWE = "owe"  # enhanced-open / opportunistic wireless encryption
    WEP_STATIC = "wep_static"  # legacy static WEP
    WEP_DYNAMIC = "wep_dynamic"  # legacy 802.1X dynamic WEP
    PSK = "psk"  # pre-shared key (WPA*-Personal)
    SAE = "sae"  # WPA3-Personal
    ENTERPRISE = "enterprise"  # 802.1X / EAP
    MPSK = "mpsk"  # multi-PSK


class WpaVersion(StrEnum):
    """WPA generation (one axis of the opmode triplet)."""

    NONE = "none"  # open / OWE / WEP carry no WPA generation
    WPA = "wpa"  # WPA1
    WPA2 = "wpa2"
    WPA3 = "wpa3"
    WPA_WPA2 = "wpa_wpa2"  # mixed WPA1+WPA2 (Central BOTH_WPA_WPA2_*)


class Cipher(StrEnum):
    """Data cipher (one axis of the opmode triplet)."""

    NONE = "none"
    WEP = "wep"
    TKIP = "tkip"
    AES_CCM = "aes_ccm"  # CCMP-128 — the standard AES default
    GCM_256 = "gcm_256"  # WPA3 192-bit
    CNSA = "cnsa"  # WPA3 Suite-B / CNSA


class MpskSource(StrEnum):
    CLOUD = "cloud"  # Central: opmode + cloud-auth, NO key copy
    LOCAL = "local"  # deferred (needs role+VLAN+PSK entries) — WLAN.md


class AuthSourceKind(StrEnum):
    RADIUS_GROUP = "radius_group"  # references a server group (own translation)
    NAC = "nac"  # references the separate NAC canonical


class VlanMode(StrEnum):
    NONE = "none"
    NAMED = "named"  # Central named-VLAN / Mist dynamic_vlan by name
    ID = "id"  # numeric VLAN id
    DYNAMIC = "dynamic"  # role-based dynamic VLAN (Mist-rich; largely unmapped)


class FastRoam(StrEnum):
    NONE = "none"
    OKC = "okc"  # Mist-only (Central has opp-key-caching separately) — preserved, unmapped
    DOT11R = "11r"  # Central dot11r ↔ Mist roam_mode "11r"


class ForwardMode(StrEnum):
    """Operator-decided target forward mode (AOS8 is per-SSID; Mist is bridged)."""

    BRIDGED = "bridged"  # Central FORWARD_MODE_BRIDGE (local breakout, no cluster)
    TUNNELED = "tunneled"  # Central FORWARD_MODE_L2 (+ overlay-wlan cluster bind)
    HYBRID = "hybrid"  # Central FORWARD_MODE_MIXED (split-tunnel, + overlay)


class RadiusServer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    host: str
    port: int | None = None
    secret: str | None = None  # tokenized in transit by the PII layer


class CoaServer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ip: str
    port: int | None = None
    secret: str | None = None


class RadiusConfig(BaseModel):
    """RADIUS detail for ``auth_source.kind == radius_group`` (or inline servers)."""

    model_config = ConfigDict(extra="forbid")
    auth_servers: list[RadiusServer] = Field(default_factory=list)
    acct_servers: list[RadiusServer] = Field(default_factory=list)
    server_selection: str | None = None  # e.g. "ordered" (primary/backup ordering)
    nas_id: str | None = None
    nas_ip: str | None = None
    coa: list[CoaServer] = Field(default_factory=list)
    radsec: bool = False
    interim_interval: int | None = None


class AuthSource(BaseModel):
    """Where an enterprise WLAN gets its auth — a *reference*, resolved by a
    separate translation (server-group or NAC). Not the auth config itself."""

    model_config = ConfigDict(extra="forbid")
    kind: AuthSourceKind
    ref: str | None = None  # server-group name / NAC profile name


class Security(BaseModel):
    """Neutral security config. The ``(key_mgmt, wpa_version, cipher)`` triplet is
    the granular opmode — readers fill it from the native opmode, the Central
    writer maps it back to a single Central opmode enum."""

    model_config = ConfigDict(extra="forbid")
    key_mgmt: KeyMgmt
    wpa_version: WpaVersion = WpaVersion.NONE
    cipher: Cipher = Cipher.AES_CCM
    wpa2_wpa3_transition: bool = False
    psk: str | None = None  # personal modes; tokenized in transit
    mpsk_source: MpskSource | None = None  # set when key_mgmt == MPSK
    mac_auth: bool = False
    auth_source: AuthSource | None = None  # set when key_mgmt == ENTERPRISE
    radius: RadiusConfig | None = None  # populated when auth_source.kind == radius_group


class Vlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mode: VlanMode = VlanMode.NONE
    name: str | None = None  # named VLAN (Central vlan-name / Mist dynamic_vlan name)
    id: int | None = None  # resolved numeric id
    # Raw dynamic-VLAN detail (Mist role→VLAN map) — largely Mist-only; kept for
    # round-trip fidelity, not fully translated.
    dynamic: dict | None = None


class Rates(BaseModel):
    """Per-band data-rate profile. WLAN.md maps g-legacy↔band_24, a-legacy↔band_5
    separately; band_6 is Mist-only. Template values: compatible|no-legacy|high-density."""

    model_config = ConfigDict(extra="forbid")
    band_24: str | None = None
    band_5: str | None = None


class Performance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dtim: int | None = None
    max_clients: int | None = None
    idle_timeout: int | None = None  # seconds
    fast_roam: FastRoam = FastRoam.NONE
    wifi7_11be: bool | None = None  # True = 11be enabled (Central EHT.enable / NOT Mist disable_11be)


class Isolation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    client_isolation: bool = False
    limit_bcast: bool = False
    arp_filter: bool = False


class Wmm(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool = True
    uapsd: bool = True


class AssignmentExceptions(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sites: list[str] = Field(default_factory=list)
    site_collections: list[str] = Field(default_factory=list)


class Assignment(BaseModel):
    """Where the WLAN is applied. Drives the writer's *create-global + assign*
    steps. Targets are NAMES (resolved to platform scope ids by the writer).

    Scope mapping (Mist ↔ Central): org-wide ↔ global; site ↔ site;
    site-group ↔ site-collection; device-profile ↔ device-group.
    """

    model_config = ConfigDict(extra="forbid")
    org_wide: bool = False
    sites: list[str] = Field(default_factory=list)
    site_collections: list[str] = Field(default_factory=list)
    device_groups: list[str] = Field(default_factory=list)
    exceptions: AssignmentExceptions = Field(default_factory=AssignmentExceptions)


class CanonicalWlan(BaseModel):
    """Platform-neutral WLAN. Readers produce it; writers consume it."""

    model_config = ConfigDict(extra="forbid")

    # --- identity ---
    ssid: str  # the broadcast SSID name
    profile_name: str | None = None  # Central profile id / Mist template name (≠ ssid)
    description: str | None = None

    # --- state ---
    enabled: bool = True
    hidden: bool = False

    # --- facets ---
    security: Security
    vlan: Vlan = Field(default_factory=Vlan)
    bands: list[str] = Field(default_factory=list)  # rf-band ↔ Mist bands (["24","5","6"])
    rates: Rates = Field(default_factory=Rates)
    performance: Performance = Field(default_factory=Performance)
    isolation: Isolation = Field(default_factory=Isolation)
    wmm: Wmm = Field(default_factory=Wmm)

    # --- forwarding / tunneling ---
    forward: ForwardMode = ForwardMode.BRIDGED  # operator-decided target
    dual_mode: bool = False  # AOS8 bridged_and_tunneled: same SSID in BOTH modes
    # Neutral names of the gateway cluster(s) a tunneled/hybrid/dual SSID tunnels
    # to (the overlay-wlan binding). Empty for bridged. The writer/orchestrator
    # resolves these names → the Central gw-cluster-list entries + scope-ids.
    gateway_clusters: list[str] = Field(default_factory=list)

    # captive portal — out of scope v1 (WLAN.md: NEEDS REVIEW). Flagged, not dropped.
    portal_deferred: bool = False

    assignment: Assignment = Field(default_factory=Assignment)
