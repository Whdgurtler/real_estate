import { ChangeEvent, FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import {
  CircleMarker,
  MapContainer,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import {
  api,
  DataFeed,
  DataFeedInput,
  DataSource,
  PortfolioSummary,
  Property,
  PriorityJurisdiction,
  SyncStatus,
  Underwriting,
  UnderwritingAssumptions,
} from "./api";

type View = "properties" | "map" | "sources";
type AnalysisPreferences = Omit<
  UnderwritingAssumptions,
  "yield_weight" | "growth_weight" | "safety_weight"
> & {
  yield_weight_percent: number;
  growth_weight_percent: number;
  safety_weight_percent: number;
};

const priorityStates = ["AR", "AL", "OH", "MO", "TX"];
const defaultPreferences: AnalysisPreferences = {
  vacancy_rate_percent: 5,
  maintenance_rate_percent: 8,
  management_rate_percent: 8,
  yield_weight_percent: 55,
  growth_weight_percent: 25,
  safety_weight_percent: 20,
};
const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});
const number = new Intl.NumberFormat("en-US");

function amount(value: number | null | undefined) {
  return value == null ? "Not supplied" : money.format(value);
}

function percent(value: number | null | undefined) {
  return value == null ? "Not available" : `${value.toFixed(1)}%`;
}

function parseStringRecord(value: string, label: string): Record<string, string> {
  let parsed: unknown;
  try {
    parsed = JSON.parse(value);
  } catch {
    throw new Error(`${label} must be valid JSON.`);
  }
  if (
    parsed == null ||
    typeof parsed !== "object" ||
    Array.isArray(parsed) ||
    Object.values(parsed).some((item) => typeof item !== "string")
  ) {
    throw new Error(`${label} must be a JSON object containing string values.`);
  }
  return parsed as Record<string, string>;
}

function isSourceType(value: string): value is Property["source_type"] {
  return [
    "conventional",
    "tax_sale",
    "code_enforcement",
    "foreclosure",
    "pre_foreclosure",
    "other",
  ].includes(value);
}

function isDataFeedConnector(value: string): value is DataFeedInput["connector"] {
  return ["socrata", "arcgis", "json_api"].includes(value);
}

function isDataFeedTarget(value: string): value is DataFeedInput["target"] {
  return ["property_leads", "property_enrichment"].includes(value);
}

function isDataFeedCategory(
  value: string,
): value is DataFeedInput["source_category"] {
  return [
    "assessor",
    "tax_sale",
    "code_enforcement",
    "foreclosure",
    "pre_foreclosure",
    "crime",
    "population",
    "pha",
    "other",
  ].includes(value);
}

function labelForSource(value: Property["source_type"]) {
  return {
    conventional: "Market listing",
    tax_sale: "Tax sale",
    code_enforcement: "Code enforcement",
    foreclosure: "Foreclosure",
    pre_foreclosure: "Pre-foreclosure",
    other: "Other lead",
  }[value];
}

function MapCenter({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, map.getZoom());
  }, [center, map]);
  return null;
}

function PropertyMap({ properties }: { properties: Property[] }) {
  const located = properties.filter(
    (property) => property.latitude != null && property.longitude != null,
  );
  const center: [number, number] = located.length
    ? [
        located.reduce((total, item) => total + (item.latitude ?? 0), 0) / located.length,
        located.reduce((total, item) => total + (item.longitude ?? 0), 0) / located.length,
      ]
    : [39.5, -98.35];

  return (
    <div className="map-frame">
      <MapContainer center={center} zoom={located.length ? 5 : 4} scrollWheelZoom>
        <MapCenter center={center} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {located.map((property) => (
          <CircleMarker
            key={property.id}
            center={[property.latitude ?? 0, property.longitude ?? 0]}
            radius={8}
            pathOptions={{ color: "#1d7469", fillColor: "#54ad9b", fillOpacity: 0.9 }}
          >
            <Popup>
              <strong>{property.address}</strong>
              <br />
              {property.city}, {property.state}
              <br />
              {amount(property.asking_price)}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      <div className="map-caption">
        {located.length
          ? `${located.length} geocoded ${located.length === 1 ? "property" : "properties"}`
          : "Add latitude and longitude to place properties on the map."}
      </div>
    </div>
  );
}

type DataSourcePanelProps = {
  sources: DataSource[];
  feeds: DataFeed[];
  jurisdictions: PriorityJurisdiction[];
  syncStatus: SyncStatus | null;
  syncing: boolean;
  onRunSync: () => void;
  onCreateFeed: (event: FormEvent<HTMLFormElement>) => void;
  onToggleFeed: (feedId: number, enabled: boolean) => void;
  onDeleteFeed: (feedId: number) => void;
};

function DataSourcePanel({
  sources,
  feeds,
  jurisdictions,
  syncStatus,
  syncing,
  onRunSync,
  onCreateFeed,
  onToggleFeed,
  onDeleteFeed,
}: DataSourcePanelProps) {
  const [feedTarget, setFeedTarget] = useState<DataFeed["target"]>("property_leads");
  const [coverageState, setCoverageState] = useState("ALL");
  const [coverageSearch, setCoverageSearch] = useState("");
  const latestRun = syncStatus?.runs[0] ?? null;
  const activeRun = syncStatus?.runs.some(
    (run) => run.status === "queued" || run.status === "running",
  );
  const visibleJurisdictions = jurisdictions.filter((jurisdiction) => {
    const matchesState = coverageState === "ALL" || jurisdiction.state === coverageState;
    const query = coverageSearch.trim().toLowerCase();
    const matchesSearch =
      !query ||
      `${jurisdiction.county} ${jurisdiction.state} ${jurisdiction.county_fips}`
        .toLowerCase()
        .includes(query);
    return matchesState && matchesSearch;
  });
  return (
    <>
      <section className="sync-panel" aria-labelledby="sync-heading">
        <div className="sync-panel-heading">
          <div>
            <span className="eyebrow">AUTOMATED REFRESH</span>
            <h3 id="sync-heading">Daily source sync</h3>
            <p>
              {syncStatus?.enabled
                ? `Scheduled daily at ${syncStatus.daily_time} ${syncStatus.timezone}.`
                : "The daily timer is disabled in server configuration."}
              {syncStatus?.next_run_at
                ? ` Next run: ${new Date(syncStatus.next_run_at).toLocaleString()}.`
                : ""}
            </p>
          </div>
          <button
            className="button button-primary"
            onClick={onRunSync}
            disabled={syncing || activeRun}
          >
            {syncing || activeRun ? "Sync queued or running…" : "Run sync now"}
          </button>
        </div>
        {latestRun && (
          <div className="sync-latest">
            <div className="sync-run-heading">
              <strong>Latest run #{latestRun.id}</strong>
              <span className={`sync-status sync-status-${latestRun.status}`}>
                {latestRun.status}
              </span>
              <span>{new Date(latestRun.started_at).toLocaleString()}</span>
              <span>{latestRun.trigger}</span>
            </div>
            {latestRun.error && <p className="sync-error">{latestRun.error}</p>}
            <div className="sync-results">
              {latestRun.source_results.map((result, index) => (
                <div className="sync-result" key={`${result.source_id}-${index}`}>
                  <strong>{result.source_name}</strong>
                  <span className={`sync-status sync-status-${result.status}`}>{result.status}</span>
                  <span>
                    {[result.source_category?.replaceAll("_", " "), result.county_fips ? `FIPS ${result.county_fips}` : null]
                      .filter(Boolean)
                      .join(" · ")}
                    {[result.source_category, result.county_fips].some(Boolean) ? " · " : ""}
                    {result.inserted} new · {result.updated} updated · {result.skipped} skipped
                  </span>
                  {(result.error || result.message) && (
                    <small>{result.error || result.message}</small>
                  )}
                  {result.warnings?.map((warning) => <small key={warning}>{warning}</small>)}
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      <section className="feed-manager" aria-labelledby="feed-heading">
        <div className="feed-heading">
          <div>
            <span className="eyebrow">JURISDICTION-SPECIFIC DATA</span>
            <h3 id="feed-heading">Configured public feeds</h3>
            <p>
              Use official city/county datasets where available. Credentials are read from server
              environment variables and are never stored in feed settings.
            </p>
          </div>
        </div>
        {feeds.length > 0 ? (
          <div className="configured-feed-list">
            {feeds.map((feed) => (
              <article className="configured-feed" key={feed.id}>
                <div>
                  <strong>{feed.name}</strong>
                  <span>
                    {feed.connector.replaceAll("_", " ")} · {feed.target.replaceAll("_", " ")} ·
                    {" "}{feed.source_category.replaceAll("_", " ")} ·
                    {" "}{feed.county_fips ? `county FIPS ${feed.county_fips} · ` : ""}
                    {feed.source_type.replaceAll("_", " ")} ·
                    {" "}{feed.max_records.toLocaleString()} records/run
                  </span>
                  <a href={feed.source_url} target="_blank" rel="noreferrer">{feed.source_url}</a>
                </div>
                <div className="feed-actions">
                  <button
                    className="button button-outline"
                    onClick={() => onToggleFeed(feed.id, !feed.enabled)}
                  >
                    {feed.enabled ? "Pause" : "Enable"}
                  </button>
                  <button
                    className="button button-outline"
                    onClick={() => onDeleteFeed(feed.id)}
                  >
                    Remove
                  </button>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <p className="empty-feed-note">No jurisdiction-specific feeds configured yet.</p>
        )}
        <details className="feed-form-details">
          <summary>Add a Socrata, ArcGIS, or JSON API feed</summary>
          <form className="feed-form" onSubmit={onCreateFeed}>
            <div className="form-grid">
              <label className="form-field">
                <span>Feed name *</span>
                <input name="name" required maxLength={200} placeholder="County code violations" />
              </label>
              <label className="form-field">
                <span>Connector *</span>
                <select name="connector" defaultValue="socrata">
                  <option value="socrata">Socrata / Open Data</option>
                  <option value="arcgis">ArcGIS FeatureServer</option>
                  <option value="json_api">JSON API</option>
                </select>
              </label>
              <label className="form-field">
                <span>Feed purpose *</span>
                <select
                  name="target"
                  value={feedTarget}
                  onChange={(event) => {
                    const value = event.target.value;
                    if (isDataFeedTarget(value)) setFeedTarget(value);
                  }}
                >
                  <option value="property_leads">Property leads (address-level)</option>
                  <option value="property_enrichment">Area enrichment (county/ZIP-level)</option>
                </select>
              </label>
              <label className="form-field">
                <span>Lead type *</span>
                <select name="source_type" defaultValue="code_enforcement">
                  <option value="conventional">Conventional</option>
                  <option value="tax_sale">Tax sale</option>
                  <option value="code_enforcement">Code enforcement</option>
                  <option value="foreclosure">Foreclosure</option>
                  <option value="pre_foreclosure">Pre-foreclosure</option>
                  <option value="other">Other</option>
                </select>
              </label>
              <label className="form-field">
                <span>Source category *</span>
                <select name="source_category" defaultValue="code_enforcement">
                  <option value="assessor">Assessor / property tax</option>
                  <option value="tax_sale">Tax sale</option>
                  <option value="code_enforcement">Code enforcement</option>
                  <option value="foreclosure">Foreclosure</option>
                  <option value="pre_foreclosure">Pre-foreclosure</option>
                  <option value="crime">Crime</option>
                  <option value="population">Population</option>
                  <option value="pha">PHA / rental assistance</option>
                  <option value="other">Other</option>
                </select>
              </label>
              <label className="form-field wide">
                <span>County jurisdiction (optional)</span>
                <select name="county_fips" defaultValue="">
                  <option value="">Unscoped / multiple counties</option>
                  {jurisdictions.map((jurisdiction) => (
                    <option key={jurisdiction.county_fips} value={jurisdiction.county_fips}>
                      {jurisdiction.county}, {jurisdiction.state} ({jurisdiction.county_fips})
                    </option>
                  ))}
                </select>
              </label>
              <label className="form-field">
                <span>Source confidence</span>
                <select name="confidence" defaultValue="official_record">
                  <option value="official_record">Official record</option>
                  <option value="official_estimate">Official estimate</option>
                  <option value="provider_estimate">Provider estimate</option>
                  <option value="user_estimate">User estimate</option>
                </select>
              </label>
              <label className="form-field">
                <span>Maximum records per run</span>
                <input name="max_records" type="number" min="1" max="5000" defaultValue="1000" />
              </label>
              <label className="form-field">
                <span>Socrata domain</span>
                <input name="domain" placeholder="data.city.gov" />
              </label>
              <label className="form-field">
                <span>Socrata dataset ID</span>
                <input name="dataset_id" placeholder="abcd-1234" />
              </label>
              <label className="form-field wide">
                <span>ArcGIS layer or JSON endpoint URL</span>
                <input name="query_url" type="url" placeholder="https://" />
              </label>
              <label className="form-field wide">
                <span>Optional source filter (SoQL or ArcGIS where clause)</span>
                <input name="where" placeholder="status = 'Open'" />
              </label>
              <label className="form-field wide">
                <span>Field mapping JSON *</span>
                <textarea
                  name="field_mapping"
                  required
                  rows={4}
                  key={feedTarget}
                  defaultValue={
                    feedTarget === "property_leads"
                      ? '{"address":"address","city":"city","state":"state"}'
                      : '{"county_fips":"county_fips","violent_crime_rate_per_100k":"violent_crime_rate_per_100k"}'
                  }
                />
              </label>
              <label className="form-field">
                <span>Record ID field</span>
                <input name="record_id_field" placeholder="case_id or objectid" />
              </label>
              <label className="form-field">
                <span>JSON API records path</span>
                <input name="records_path" placeholder="results (blank for root array)" />
              </label>
              <label className="form-field wide">
                <span>JSON API query parameters</span>
                <textarea name="query_params" rows={2} placeholder='{"state":"Arkansas","family":"lien"}' />
              </label>
              <label className="form-field">
                <span>API credential environment variable</span>
                <input name="auth_env_var" placeholder="TAXLIENSIMPLE_API_KEY" />
              </label>
              <label className="form-field">
                <span>API-key query parameter (optional)</span>
                <input name="auth_query_param" placeholder="api_key" />
              </label>
            </div>
            <p className="feed-form-note">
              Lead feeds need address, city, and state. Area enrichment needs county FIPS, ZIP plus
              state, or county plus state, and may only update area-level rent, PHA, crime, or
              population metrics. JSON API pagination uses limit/offset when supported. Validate
              licensing and source terms before enabling a feed.
            </p>
            <button className="button button-primary" type="submit">Save feed</button>
          </form>
        </details>
      </section>

      <section className="county-coverage" aria-labelledby="county-coverage-heading">
        <div className="feed-heading">
          <div>
            <span className="eyebrow">PRIORITY-STATE SOURCE DIRECTORY</span>
            <h3 id="county-coverage-heading">
              County-level acquisition sources
            </h3>
            <p>
              {jurisdictions.length} Census county-equivalents across Arkansas, Alabama, Ohio, and
              Missouri. Directories help locate each office; a directory link is not an automated
              data feed. Configure a feed for the county and source category after verifying its
              endpoint and terms.
            </p>
          </div>
        </div>
        <div className="county-coverage-controls">
          <select
            aria-label="Filter counties by state"
            value={coverageState}
            onChange={(event) => setCoverageState(event.target.value)}
          >
            <option value="ALL">All priority states ({jurisdictions.length})</option>
            {priorityStates.map((state) => (
              <option key={state} value={state}>
                {state} ({jurisdictions.filter((jurisdiction) => jurisdiction.state === state).length})
              </option>
            ))}
          </select>
          <input
            aria-label="Search counties"
            value={coverageSearch}
            onChange={(event) => setCoverageSearch(event.target.value)}
            placeholder="Search county or FIPS"
          />
          <span>{visibleJurisdictions.length} shown</span>
        </div>
        <div className="county-coverage-list">
          {visibleJurisdictions.map((jurisdiction) => (
            <details className="county-source-entry" key={jurisdiction.county_fips}>
              <summary>
                <strong>{jurisdiction.county}</strong>
                <span>{jurisdiction.state}</span>
                <code>{jurisdiction.county_fips}</code>
                <span>
                  {Object.values(jurisdiction.sources).filter((source) => source.configured).length}
                  /{Object.keys(jurisdiction.sources).length} feeds configured
                </span>
              </summary>
              <div className="county-source-grid">
                {Object.entries(jurisdiction.sources).map(([category, source]) => (
                  <article className="county-source-card" key={category}>
                    <div className="county-source-card-top">
                      <strong>{category.replaceAll("_", " ")}</strong>
                      <span className={`sync-status sync-status-${source.configured ? "success" : source.status === "feed_paused" || source.endpoint_url ? "partial" : "queued"}`}>
                        {source.configured
                          ? "feed configured"
                          : source.status === "feed_paused"
                            ? "feed paused"
                            : source.endpoint_url
                              ? source.endpoint_status === "restricted_planning"
                                ? "tested; restricted"
                                : source.endpoint_status === "historical_not_daily"
                                  ? "tested; historical"
                                  : source.endpoint_status === "freshness_review_required"
                                    ? "tested; freshness unknown"
                                : "tested; review required"
                              : "endpoint needed"}
                      </span>
                    </div>
                    <p>{source.note}</p>
                    <div className="county-source-links">
                      <a href={source.source_url} target="_blank" rel="noreferrer">
                        Open {source.directory_name} ↗
                      </a>
                      <a href={source.search_url} target="_blank" rel="noreferrer">
                        Search this county ↗
                      </a>
                      {source.endpoint_url && (
                        <a href={source.endpoint_url} target="_blank" rel="noreferrer">
                          Open tested API endpoint ↗
                        </a>
                      )}
                      {source.endpoint_info_url && (
                        <a href={source.endpoint_info_url} target="_blank" rel="noreferrer">
                          Review publisher details ↗
                        </a>
                      )}
                    </div>
                    {source.endpoint_note && (
                      <p>
                        <small>
                          Tested {source.endpoint_last_verified}
                          {source.endpoint_record_count !== undefined &&
                            ` · ${source.endpoint_record_count.toLocaleString()} records`}
                          {source.endpoint_scope && ` · ${source.endpoint_scope}`}
                          {`: ${source.endpoint_note}`}
                        </small>
                      </p>
                    )}
                    {source.additional_endpoints?.map((endpoint) => (
                      <div key={endpoint.url}>
                        <div className="county-source-links">
                          <a href={endpoint.url} target="_blank" rel="noreferrer">
                            Open {endpoint.name} API ↗
                          </a>
                          {endpoint.info_url && (
                            <a href={endpoint.info_url} target="_blank" rel="noreferrer">
                              Review publisher details ↗
                            </a>
                          )}
                        </div>
                        <p>
                          <small>
                            Tested {endpoint.last_verified}
                            {endpoint.record_count !== undefined &&
                              ` · ${endpoint.record_count.toLocaleString()} records`}
                            {endpoint.scope && ` · ${endpoint.scope}`}
                            {`: ${endpoint.note}`}
                          </small>
                        </p>
                      </div>
                    ))}
                    {source.feeds.map((feed) => (
                      <span className="county-feed-name" key={feed.id}>
                        {feed.enabled ? "Enabled" : "Paused"}: {feed.name}
                      </span>
                    ))}
                  </article>
                ))}
              </div>
            </details>
          ))}
        </div>
      </section>

      <div className="source-grid">
        {sources.map((source) => (
          <article className="source-card" key={source.id}>
            <div className="source-card-top">
              <span className="source-category">{source.category.replaceAll("_", " ")}</span>
              <span className={`availability availability-${source.availability}`}>
                {source.availability.replaceAll("_", " ")}
              </span>
            </div>
            <h3>{source.name}</h3>
            <p>{source.access}</p>
            {source.url && (
              <a href={source.url} target="_blank" rel="noreferrer">
                Open source <span aria-hidden="true">↗</span>
              </a>
            )}
          </article>
        ))}
      </div>
    </>
  );
}

function App() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [sources, setSources] = useState<DataSource[]>([]);
  const [feeds, setFeeds] = useState<DataFeed[]>([]);
  const [jurisdictions, setJurisdictions] = useState<PriorityJurisdiction[]>([]);
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [underwriting, setUnderwriting] = useState<Underwriting | null>(null);
  const [analysisPreferences, setAnalysisPreferences] =
    useState<AnalysisPreferences>(defaultPreferences);
  const [activeView, setActiveView] = useState<View>("properties");
  const [activeState, setActiveState] = useState("ALL");
  const [search, setSearch] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const refreshDashboard = useCallback(async () => {
    setLoading(true);
    try {
      const [propertyRows, sourceRows, portfolio, feedRows, status, countyDirectory] = await Promise.all([
        api.properties(),
        api.dataSources(),
        api.summary(),
        api.dataFeeds(),
        api.syncStatus(),
        api.jurisdictions(),
      ]);
      setProperties(propertyRows);
      setSources(sourceRows);
      setSummary(portfolio);
      setFeeds(feedRows);
      setSyncStatus(status);
      setJurisdictions(countyDirectory.jurisdictions);
      setSelectedId((current) => current ?? propertyRows[0]?.id ?? null);
      setError(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshDashboard().catch((reason: unknown) => {
      setError(reason instanceof Error ? reason.message : "Could not load the dashboard.");
    });
  }, [refreshDashboard]);

  useEffect(() => {
    if (activeView !== "sources") return;
    const timer = window.setInterval(() => {
      api
        .syncStatus()
        .then(setSyncStatus)
        .catch((reason: unknown) => {
          setError(reason instanceof Error ? reason.message : "Could not refresh sync status.");
        });
    }, 10000);
    return () => window.clearInterval(timer);
  }, [activeView]);

  useEffect(() => {
    if (selectedId == null) {
      setUnderwriting(null);
      return;
    }
    const totalWeight =
      analysisPreferences.yield_weight_percent +
      analysisPreferences.growth_weight_percent +
      analysisPreferences.safety_weight_percent;
    if (totalWeight <= 0) {
      setUnderwriting(null);
      return;
    }
    let current = true;
    setUnderwriting(null);
    api
      .underwriting(selectedId, {
        vacancy_rate_percent: analysisPreferences.vacancy_rate_percent,
        maintenance_rate_percent: analysisPreferences.maintenance_rate_percent,
        management_rate_percent: analysisPreferences.management_rate_percent,
        yield_weight: analysisPreferences.yield_weight_percent / 100,
        growth_weight: analysisPreferences.growth_weight_percent / 100,
        safety_weight: analysisPreferences.safety_weight_percent / 100,
      })
      .then((result) => {
        if (current) setUnderwriting(result);
      })
      .catch((reason: unknown) => {
        if (current) {
          setError(reason instanceof Error ? reason.message : "Could not calculate underwriting.");
        }
      });
    return () => {
      current = false;
    };
  }, [analysisPreferences, selectedId]);

  const selectedProperty = properties.find((property) => property.id === selectedId) ?? null;
  const editingProperty = properties.find((property) => property.id === editingId) ?? null;
  const states = useMemo(
    () =>
      Array.from(new Set(properties.map((property) => property.state))).sort((a, b) => {
        const aPriority = priorityStates.indexOf(a);
        const bPriority = priorityStates.indexOf(b);
        if (aPriority >= 0 || bPriority >= 0) {
          if (aPriority < 0) return 1;
          if (bPriority < 0) return -1;
          return aPriority - bPriority;
        }
        return a.localeCompare(b);
      }),
    [properties],
  );
  const visibleProperties = useMemo(() => {
    const term = search.trim().toLowerCase();
    const parsedMaximum = maxPrice.trim() ? Number(maxPrice) : null;
    const maximum = parsedMaximum != null && Number.isFinite(parsedMaximum) ? parsedMaximum : null;
    return properties.filter((property) => {
      const matchesState = activeState === "ALL" || property.state === activeState;
      const matchesPrice =
        maximum == null || (property.asking_price != null && property.asking_price <= maximum);
      const matchesTerm =
        !term ||
        [property.address, property.city, property.state, property.county, property.zip_code]
          .some((value) => value?.toLowerCase().includes(term));
      return matchesState && matchesTerm && matchesPrice;
    });
  }, [activeState, maxPrice, properties, search]);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    setNotice(null);
    const form = new FormData(event.currentTarget);
    const text = (key: string) => String(form.get(key) ?? "").trim();
    const numeric = (key: string) => {
      const value = text(key);
      return value ? Number(value) : null;
    };
    const sourceMetadata: Record<
      string,
      { source_name: string; source_url: string | null; confidence: string }
    > = {};
    const addSource = (group: string, nameKey: string, urlKey: string) => {
      const sourceName = text(nameKey);
      const sourceUrl = text(urlKey);
      if (sourceName || sourceUrl) {
        sourceMetadata[group] = {
          source_name: sourceName || "User-provided",
          source_url: sourceUrl || null,
          confidence: "user_provided",
        };
      }
    };
    addSource("tax", "tax_source_name", "tax_source_url");
    addSource("insurance", "insurance_source", "insurance_source_url");
    addSource("market_rent", "market_rent_source_name", "market_rent_source_url");
    addSource("hud_fmr", "hud_source_name", "hud_source_url");
    addSource("pha", "pha_source_name", "pha_source_url");
    addSource("neighborhood", "neighborhood_source_name", "neighborhood_source_url");
    const payload: Record<string, unknown> = {
      address: text("address"),
      city: text("city"),
      state: text("state").toUpperCase(),
      zip_code: text("zip_code") || null,
      county: text("county") || null,
      county_fips: text("county_fips") || null,
      latitude: numeric("latitude"),
      longitude: numeric("longitude"),
      source_type: text("source_type"),
      source_name: text("source_name") || null,
      source_url: text("source_url") || null,
      source_metadata: sourceMetadata,
      asking_price: numeric("asking_price"),
      estimated_repairs: numeric("estimated_repairs"),
      bedrooms: numeric("bedrooms"),
      bathrooms: numeric("bathrooms"),
      square_feet: numeric("square_feet"),
      year_built: numeric("year_built"),
      annual_property_tax: numeric("annual_property_tax"),
      assessed_value: numeric("assessed_value"),
      tax_rate_percent: numeric("tax_rate_percent"),
      annual_insurance_estimate: numeric("annual_insurance_estimate"),
      insurance_source: text("insurance_source") || null,
      expected_market_rent_monthly: numeric("expected_market_rent_monthly"),
      hud_fmr_monthly: numeric("hud_fmr_monthly"),
      pha_payment_standard_monthly: numeric("pha_payment_standard_monthly"),
      pha_name: text("pha_name") || null,
      pha_id: text("pha_id") || null,
      pha_program_status: text("pha_program_status"),
      voucher_waitlist_status: text("voucher_waitlist_status"),
      open_voucher_count: numeric("open_voucher_count"),
      population_growth_percent: numeric("population_growth_percent"),
      violent_crime_rate_per_100k: numeric("violent_crime_rate_per_100k"),
    };
    try {
      const saved =
        editingId == null
          ? await api.createProperty(payload)
          : await api.updateProperty(editingId, payload);
      setProperties((current) =>
        editingId == null
          ? [saved, ...current]
          : current.map((property) => (property.id === saved.id ? saved : property)),
      );
      setSelectedId(saved.id);
      const previousState = properties.find((property) => property.id === editingId)?.state;
      if (editingId == null || previousState !== saved.state) setActiveState("ALL");
      setEditingId(null);
      setShowForm(false);
      setNotice(
        editingId == null
          ? "Property added. Estimates and data gaps are shown in its underwriting."
          : "Property details updated; the evidence ledger keeps the submitted source trail.",
      );
      await refreshDashboard();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not save the property.");
    } finally {
      setSaving(false);
    }
  }

  async function handleImport(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setError(null);
    setNotice(null);
    try {
      const result = await api.importCsv(await file.text());
      await refreshDashboard();
      setNotice(`${result.imported} ${result.imported === 1 ? "property" : "properties"} imported.`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "CSV import failed.");
    }
  }

  async function handleCreateFeed(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    const text = (key: string) => String(form.get(key) ?? "").trim();
    const connectorValue = text("connector");
    const targetValue = text("target");
    const categoryValue = text("source_category");
    const sourceTypeValue = text("source_type");
    setError(null);
    setNotice(null);
    try {
      if (!isDataFeedConnector(connectorValue)) {
        throw new Error("Select a supported data feed connector.");
      }
      if (!isDataFeedTarget(targetValue)) {
        throw new Error("Select a supported feed purpose.");
      }
      if (!isDataFeedCategory(categoryValue)) {
        throw new Error("Select a supported source category.");
      }
      if (!isSourceType(sourceTypeValue)) {
        throw new Error("Select a supported property lead type.");
      }
      const maxRecords = Number(text("max_records"));
      if (!Number.isInteger(maxRecords) || maxRecords < 1 || maxRecords > 5000) {
        throw new Error("Maximum records must be an integer from 1 to 5,000.");
      }
      const payload: DataFeedInput = {
        name: text("name"),
        connector: connectorValue,
        target: targetValue,
        source_category: categoryValue,
        source_type: sourceTypeValue,
        enabled: true,
        confidence: text("confidence"),
        field_mapping: parseStringRecord(text("field_mapping"), "Field mapping"),
        max_records: maxRecords,
        query_params: parseStringRecord(text("query_params") || "{}", "Query parameters"),
      };
      const optionalFields = [
        "domain",
        "dataset_id",
        "query_url",
        "where",
        "record_id_field",
        "records_path",
        "auth_env_var",
        "auth_query_param",
        "county_fips",
      ] as const;
      for (const field of optionalFields) {
        const value = text(field);
        if (value) payload[field] = value;
      }
      await api.createDataFeed(payload);
      await refreshDashboard();
      formElement.reset();
      setNotice("Daily data feed saved. It will run on the configured schedule.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not save the data feed.");
    }
  }

  async function handleRunSync() {
    setError(null);
    setNotice(null);
    setSyncing(true);
    try {
      const result = await api.runSync();
      setNotice(`Data sync #${result.run_id} was queued.`);
      setSyncStatus(await api.syncStatus());
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not queue the data sync.");
    } finally {
      setSyncing(false);
    }
  }

  async function handleToggleFeed(feedId: number, enabled: boolean) {
    setError(null);
    try {
      await api.updateDataFeed(feedId, enabled);
      await refreshDashboard();
      setNotice(enabled ? "Data feed enabled." : "Data feed paused.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not update the data feed.");
    }
  }

  async function handleDeleteFeed(feedId: number) {
    if (!window.confirm("Remove this feed configuration? Previously imported properties will remain.")) {
      return;
    }
    setError(null);
    try {
      await api.deleteDataFeed(feedId);
      await refreshDashboard();
      setNotice("Data feed configuration removed. Imported properties were retained.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not remove the data feed.");
    }
  }

  async function refreshPopulation() {
    if (!selectedProperty) return;
    setError(null);
    setNotice(null);
    try {
      const enriched = await api.census(selectedProperty.id);
      setProperties((current) =>
        current.map((property) => (property.id === enriched.id ? enriched : property)),
      );
      setNotice(
        `Population growth updated from the Census ACS ${enriched.population_data_year} 5-year estimate.`,
      );
      const totalWeight =
        analysisPreferences.yield_weight_percent +
        analysisPreferences.growth_weight_percent +
        analysisPreferences.safety_weight_percent;
      if (totalWeight > 0) {
        setUnderwriting(
          await api.underwriting(enriched.id, {
            vacancy_rate_percent: analysisPreferences.vacancy_rate_percent,
            maintenance_rate_percent: analysisPreferences.maintenance_rate_percent,
            management_rate_percent: analysisPreferences.management_rate_percent,
            yield_weight: analysisPreferences.yield_weight_percent / 100,
            growth_weight: analysisPreferences.growth_weight_percent / 100,
            safety_weight: analysisPreferences.safety_weight_percent / 100,
          }),
        );
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Census enrichment failed.");
    }
  }

  const distressedCount =
    (summary?.lead_types.tax_sale ?? 0) +
    (summary?.lead_types.code_enforcement ?? 0) +
    (summary?.lead_types.foreclosure ?? 0) +
    (summary?.lead_types.pre_foreclosure ?? 0);
  const averageAskingPrice = properties.filter((property) => property.asking_price != null);
  const averagePrice = averageAskingPrice.length
    ? averageAskingPrice.reduce((total, property) => total + (property.asking_price ?? 0), 0) /
      averageAskingPrice.length
    : null;
  const score = underwriting?.score;
  const section8 = underwriting?.section8;
  const scoreWeightsTotal =
    analysisPreferences.yield_weight_percent +
    analysisPreferences.growth_weight_percent +
    analysisPreferences.safety_weight_percent;
  const scoreWeightsInvalid = scoreWeightsTotal <= 0;

  function openAddForm() {
    setEditingId(null);
    setShowForm(true);
  }

  function openEditForm() {
    if (!selectedProperty) return;
    setEditingId(selectedProperty.id);
    setShowForm(true);
  }

  function updateAnalysisPreference(key: keyof AnalysisPreferences, value: string) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed) || parsed < 0 || parsed > 100) return;
    setAnalysisPreferences((current) => ({ ...current, [key]: parsed }));
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">G</div>
          <div>
            <strong>groundwork</strong>
            <span>PROPERTY INTELLIGENCE</span>
          </div>
        </div>
        <div className="workspace-label">WORKSPACE</div>
        <nav className="navigation" aria-label="Main navigation">
          <button
            className={activeView === "properties" ? "nav-item active" : "nav-item"}
            onClick={() => setActiveView("properties")}
          >
            <span className="nav-icon">⌂</span> Deal pipeline
            <span className="nav-count">{summary?.property_count ?? 0}</span>
          </button>
          <button
            className={activeView === "map" ? "nav-item active" : "nav-item"}
            onClick={() => setActiveView("map")}
          >
            <span className="nav-icon">◎</span> Opportunity map
          </button>
          <button
            className={activeView === "sources" ? "nav-item active" : "nav-item"}
            onClick={() => setActiveView("sources")}
          >
            <span className="nav-icon">▤</span> Data sources
          </button>
        </nav>
        <div className="sidebar-bottom">
          <div className="priority-note">
            <span className="priority-dot" />
            <div>
              <strong>Priority markets</strong>
              <span>AR · AL · OH · MO</span>
            </div>
          </div>
          <div className="profile">
            <div className="avatar">RE</div>
            <div><strong>Investment desk</strong><span>Single-operator workspace</span></div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb"><span>Workspace</span><b>/</b> Acquisition pipeline</div>
          <div className="topbar-actions">
            <span className="live-badge"><span /> Sources tracked</span>
            <button className="button button-primary" onClick={openAddForm}>
              <span aria-hidden="true">＋</span> Add opportunity
            </button>
          </div>
        </header>

        <div className="page-content">
          <section className="page-heading">
            <div>
              <p className="eyebrow">NATIONAL DEALFLOW · PRIORITY STATES FIRST</p>
              <h1>Find the right property.<br /><em>Know the whole picture.</em></h1>
              <p className="page-subtitle">
                Bring leads, neighborhood signals, ownership costs, and voucher-rent benchmarks into one decision workspace.
              </p>
            </div>
            <div className="heading-mark" aria-hidden="true">⌂</div>
          </section>

          {error && (
            <div className="alert alert-error" role="alert">
              <span><strong>Something needs attention.</strong> {error}</span>
              <button onClick={() => setError(null)} aria-label="Dismiss error">×</button>
            </div>
          )}
          {notice && (
            <div className="alert alert-success" role="status">
              <span>{notice}</span>
              <button onClick={() => setNotice(null)} aria-label="Dismiss notice">×</button>
            </div>
          )}

          <section className="metrics-grid" aria-label="Portfolio overview">
            <article className="metric-card">
              <span className="metric-icon icon-mint">⌂</span>
              <div className="metric-label">Tracked opportunities</div>
              <div className="metric-value">{summary?.property_count ?? "—"}</div>
              <div className="metric-foot">Across {Object.keys(summary?.states ?? {}).length || "all"} active markets</div>
            </article>
            <article className="metric-card">
              <span className="metric-icon icon-amber">↗</span>
              <div className="metric-label">Distressed leads</div>
              <div className="metric-value">{distressedCount}</div>
              <div className="metric-foot">Tax sale and code enforcement</div>
            </article>
            <article className="metric-card">
              <span className="metric-icon icon-blue">$</span>
              <div className="metric-label">Average asking price</div>
              <div className="metric-value metric-price">{averagePrice == null ? "—" : amount(averagePrice)}</div>
              <div className="metric-foot">{averageAskingPrice.length} priced opportunities</div>
            </article>
            <article className="metric-card">
              <span className="metric-icon icon-rose">!</span>
              <div className="metric-label">Needs verification</div>
              <div className="metric-value">{summary?.voucher_counts_unknown ?? "—"}</div>
              <div className="metric-foot">Voucher counts not published or entered</div>
            </article>
          </section>

          <section className="workspace-card">
            <div className="workspace-toolbar">
              <div>
                <div className="section-kicker">YOUR PIPELINE</div>
                <h2>{activeView === "sources" ? "Data coverage" : activeView === "map" ? "Opportunity map" : "Property opportunities"}</h2>
              </div>
              {activeView === "properties" && (
                <div className="toolbar-controls">
                  <label className="search-box">
                    <span aria-hidden="true">⌕</span>
                    <input
                      aria-label="Search opportunities"
                      placeholder="Search address, city, county..."
                      value={search}
                      onChange={(event) => setSearch(event.target.value)}
                    />
                  </label>
                  <select
                    aria-label="Filter by state"
                    value={activeState}
                    onChange={(event) => setActiveState(event.target.value)}
                  >
                    <option value="ALL">All states</option>
                    {states.map((state) => <option key={state} value={state}>{state}</option>)}
                  </select>
                  <input
                    aria-label="Maximum asking price"
                    className="price-filter"
                    type="number"
                    min="0"
                    placeholder="Max price"
                    value={maxPrice}
                    onChange={(event) => setMaxPrice(event.target.value)}
                  />
                  <label className="button button-outline import-button">
                    Import CSV
                    <input type="file" accept=".csv,text/csv" onChange={handleImport} />
                  </label>
                </div>
              )}
            </div>

            {activeView === "sources" ? (
              <div className="source-content">
                <div className="coverage-intro">
                  <div className="coverage-symbol">◉</div>
                  <div>
                    <h3>Know what is known—and what is not.</h3>
                    <p>Public data coverage changes by agency and county. Each record keeps its source, date, and confidence so an estimate never masquerades as a verified fact.</p>
                  </div>
                </div>
                <DataSourcePanel
                  sources={sources}
                  feeds={feeds}
                  jurisdictions={jurisdictions}
                  syncStatus={syncStatus}
                  syncing={syncing}
                  onRunSync={() => void handleRunSync()}
                  onCreateFeed={(event) => void handleCreateFeed(event)}
                  onToggleFeed={(feedId, enabled) => void handleToggleFeed(feedId, enabled)}
                  onDeleteFeed={(feedId) => void handleDeleteFeed(feedId)}
                />
              </div>
            ) : activeView === "map" ? (
              <div className="map-content">
                <div className="map-header">
                  <p>Only properties with coordinates appear as markers. Add latitude and longitude when entering a lead.</p>
                  <select aria-label="Filter map by state" value={activeState} onChange={(event) => setActiveState(event.target.value)}>
                    <option value="ALL">All states</option>
                    {states.map((state) => <option key={state} value={state}>{state}</option>)}
                  </select>
                </div>
                <PropertyMap properties={visibleProperties} />
              </div>
            ) : (
              <div className="deal-layout">
                <div className="deal-list">
                  <div className="list-heading">
                    <span>{loading ? "Loading opportunities..." : `${visibleProperties.length} ${visibleProperties.length === 1 ? "opportunity" : "opportunities"}`}</span>
                    <span className="sort-label">Recently added <span aria-hidden="true">⌄</span></span>
                  </div>
                  {visibleProperties.map((property) => (
                    <button
                      className={property.id === selectedId ? "deal-card selected" : "deal-card"}
                      key={property.id}
                      onClick={() => setSelectedId(property.id)}
                    >
                      <div className="deal-card-top">
                        <span className={`type-pill type-${property.source_type}`}>{labelForSource(property.source_type)}</span>
                        <span className="deal-state">{property.state}</span>
                      </div>
                      <strong className="deal-address">{property.address}</strong>
                      <span className="deal-location">{property.city}{property.county ? ` · ${property.county} County` : ""}</span>
                      <div className="deal-card-bottom">
                        <span>{amount(property.asking_price)}</span>
                        <span>{property.bedrooms == null ? "Beds —" : `${property.bedrooms} bd`} · {property.square_feet == null ? "— sqft" : `${number.format(property.square_feet)} sqft`}</span>
                      </div>
                    </button>
                  ))}
                  {!loading && visibleProperties.length === 0 && (
                    <div className="empty-state">
                      <div className="empty-icon">⌂</div>
                      <h3>{properties.length ? "No matching opportunities" : "Your pipeline starts here"}</h3>
                      <p>{properties.length ? "Try a different search or state filter." : "Add a lead manually or import a county/listing CSV to begin comparing properties."}</p>
                      {!properties.length && <button className="button button-primary" onClick={openAddForm}>Add your first lead</button>}
                    </div>
                  )}
                </div>

                <div className="detail-panel">
                  {selectedProperty ? (
                    <>
                      <div className="detail-top">
                        <div>
                          <span className={`type-pill type-${selectedProperty.source_type}`}>{labelForSource(selectedProperty.source_type)}</span>
                          <h3>{selectedProperty.address}</h3>
                          <p>{selectedProperty.city}, {selectedProperty.state}{selectedProperty.zip_code ? ` ${selectedProperty.zip_code}` : ""}</p>
                        </div>
                        <div className="detail-actions">
                          <button className="edit-record-button" onClick={openEditForm}>Edit inputs</button>
                          <div className="score-badge" title="Weighted, partial-data score; not an investment recommendation">
                            <strong>{score?.overall == null ? "—" : Math.round(score.overall)}</strong>
                            <span>DEAL<br />SIGNAL</span>
                          </div>
                        </div>
                      </div>
                      <div className="detail-facts">
                        <div><span>Asking price</span><strong>{amount(selectedProperty.asking_price)}</strong></div>
                        <div><span>Repairs (entered)</span><strong>{amount(selectedProperty.estimated_repairs)}</strong></div>
                        <div><span>Annualized population growth</span><strong>{percent(selectedProperty.population_growth_percent)}</strong></div>
                        <div><span>Violent crime / 100k</span><strong>{selectedProperty.violent_crime_rate_per_100k == null ? "Not available" : number.format(selectedProperty.violent_crime_rate_per_100k)}</strong></div>
                      </div>

                      <div className="detail-section">
                        <div className="subheading"><h4>Rental underwriting</h4><span className="subheading-tag">PRE-FINANCING</span></div>
                        {underwriting ? (
                          <>
                            <div className="underwriting-row">
                              <div>
                                <span className="scenario-label">Section 8 planning benchmark</span>
                                <strong>{amount(section8?.scenario.rent_monthly)}</strong>
                              </div>
                              <div className="underwriting-stat">
                                <span>Monthly cash flow</span>
                                <strong>{section8?.scenario.monthly_operating_cash_flow_before_financing_and_hoa == null ? "Incomplete" : amount(section8.scenario.monthly_operating_cash_flow_before_financing_and_hoa)}</strong>
                              </div>
                            </div>
                            <p className="detail-note">{section8?.benchmark_basis}. Rent benchmarks are not an approved contract rent or subsidy amount. Cap rate basis: {section8?.scenario.capital_basis_note}.</p>
                            <div className="cost-grid">
                              <div><span>Annual property tax</span><strong>{amount(underwriting.property_tax_annual)}</strong></div>
                              <div><span>Annual insurance</span><strong>{amount(underwriting.insurance_annual)}</strong></div>
                              <div><span>Open voucher count</span><strong>{section8?.open_voucher_count == null ? "Unknown" : number.format(section8.open_voucher_count)}</strong></div>
                              <div><span>PHA program</span><strong>{section8?.program_status === "confirmed" ? "Confirmed" : "Unverified"}</strong></div>
                            </div>
                            {section8 && !section8.scenario.complete_for_displayed_costs && (
                              <div className="missing-data">
                                <span>○</span>
                                <p><strong>Incomplete estimate:</strong> {section8.scenario.missing_inputs.join("; ")}.</p>
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="loading-inline">{scoreWeightsInvalid ? "Choose at least one score weight above zero." : "Calculating from supplied inputs…"}</div>
                        )}
                      </div>

                      <div className="detail-section score-section">
                        <div className="subheading"><h4>Neighborhood &amp; score</h4><span className="coverage-label">{score ? `${Math.round(score.coverage * 100)}% data coverage` : "Waiting for data"}</span></div>
                        <div className="score-bars">
                          <div className="score-line"><span>Rental yield</span><div className="bar-track"><div className="bar-fill" style={{ width: `${score?.components.yield ?? 0}%` }} /></div><b>{score?.components.yield == null ? "—" : Math.round(score.components.yield)}</b></div>
                          <div className="score-line"><span>Population growth</span><div className="bar-track"><div className="bar-fill bar-blue" style={{ width: `${score?.components.population_growth ?? 0}%` }} /></div><b>{score?.components.population_growth == null ? "—" : Math.round(score.components.population_growth)}</b></div>
                          <div className="score-line"><span>Crime safety signal</span><div className="bar-track"><div className="bar-fill bar-gold" style={{ width: `${score?.components.crime_safety ?? 0}%` }} /></div><b>{score?.components.crime_safety == null ? "—" : Math.round(score.components.crime_safety)}</b></div>
                        </div>
                        <p className="detail-note">Weighted heuristic, bounded to 0–100; missing inputs are excluded and reduce data coverage. Not an investment recommendation.</p>
                        <details className="assumptions-panel">
                          <summary>Adjust operating reserves &amp; score weights</summary>
                          <div className="assumptions-grid">
                            <label>Vacancy reserve (%)<input type="number" min="0" max="100" step="1" value={analysisPreferences.vacancy_rate_percent} onChange={(event) => updateAnalysisPreference("vacancy_rate_percent", event.target.value)} /></label>
                            <label>Maintenance reserve (%)<input type="number" min="0" max="100" step="1" value={analysisPreferences.maintenance_rate_percent} onChange={(event) => updateAnalysisPreference("maintenance_rate_percent", event.target.value)} /></label>
                            <label>Management reserve (%)<input type="number" min="0" max="100" step="1" value={analysisPreferences.management_rate_percent} onChange={(event) => updateAnalysisPreference("management_rate_percent", event.target.value)} /></label>
                            <label>Yield weight (%)<input type="number" min="0" max="100" step="1" value={analysisPreferences.yield_weight_percent} onChange={(event) => updateAnalysisPreference("yield_weight_percent", event.target.value)} /></label>
                            <label>Population weight (%)<input type="number" min="0" max="100" step="1" value={analysisPreferences.growth_weight_percent} onChange={(event) => updateAnalysisPreference("growth_weight_percent", event.target.value)} /></label>
                            <label>Crime-safety weight (%)<input type="number" min="0" max="100" step="1" value={analysisPreferences.safety_weight_percent} onChange={(event) => updateAnalysisPreference("safety_weight_percent", event.target.value)} /></label>
                          </div>
                          {scoreWeightsInvalid
                            ? <p className="assumption-warning">At least one score weight must be greater than zero.</p>
                            : <p className="assumption-help">Weights are normalized across the available data factors. Changes recalculate the current analysis.</p>}
                        </details>
                        {selectedProperty.county_fips && (
                          <button className="text-button" onClick={() => void refreshPopulation()}>
                            Refresh county population from Census ACS <span aria-hidden="true">↗</span>
                          </button>
                        )}
                      </div>

                      <div className="detail-section evidence-section">
                        <div className="subheading"><h4>Evidence ledger</h4><span className="coverage-label">{selectedProperty.evidence.length} recorded figures</span></div>
                        {selectedProperty.evidence.length ? (
                          <div className="evidence-list">
                            {[...selectedProperty.evidence].reverse().slice(0, 8).map((item) => (
                              <div className="evidence-item" key={item.id}>
                                <div className="evidence-item-heading">
                                  <strong>{item.metric.replaceAll("_", " ")}</strong>
                                  <span>{item.value}</span>
                                </div>
                                <div className="evidence-item-source">
                                  <span>{item.source_name} · {new Date(item.observed_at).toLocaleDateString()} · {item.confidence.replaceAll("_", " ")}</span>
                                  {item.source_url && <a href={item.source_url} target="_blank" rel="noreferrer">Source ↗</a>}
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="detail-note">No sourced metric evidence has been recorded yet. Add source details with values or import a sourced record.</p>
                        )}
                      </div>

                      <div className="detail-footer">
                        <span>Lead source: {selectedProperty.source_name || "Not specified"}</span>
                        {selectedProperty.source_url && <a href={selectedProperty.source_url} target="_blank" rel="noreferrer">View source ↗</a>}
                      </div>
                    </>
                  ) : (
                    <div className="empty-detail">
                      <div className="empty-icon">◌</div>
                      <h3>Select an opportunity</h3>
                      <p>Property evidence and rental analysis will appear here.</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </section>

          <footer className="page-footer">
            <span>Groundwork <span>·</span> Source-aware real estate research</span>
            <span>Estimates are for screening only. Verify local requirements, agency rules, and property condition.</span>
          </footer>
        </div>
      </main>

      {showForm && (
        <div className="modal-backdrop" role="presentation" onMouseDown={(event) => {
          if (event.target === event.currentTarget) setShowForm(false);
        }}>
          <section className="property-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
            <div className="modal-heading">
              <div><span className="eyebrow">{editingProperty ? "UPDATE PROPERTY LEAD" : "NEW PROPERTY LEAD"}</span><h2 id="modal-title">{editingProperty ? "Edit opportunity" : "Add an opportunity"}</h2></div>
              <button className="modal-close" onClick={() => setShowForm(false)} aria-label="Close form">×</button>
            </div>
            <p className="modal-intro">Enter what you know. Missing costs and unpublished voucher data remain explicitly unknown.</p>
            <form onSubmit={(event) => void handleCreate(event)}>
              <div className="form-section-title">Property &amp; source</div>
              <div className="form-grid">
                <label className="form-field wide"><span>Street address *</span><input name="address" required maxLength={300} defaultValue={editingProperty?.address ?? ""} /></label>
                <label className="form-field"><span>City *</span><input name="city" required defaultValue={editingProperty?.city ?? ""} /></label>
                <label className="form-field small"><span>State *</span><input name="state" required maxLength={2} defaultValue={editingProperty?.state ?? "AR"} /></label>
                <label className="form-field"><span>County</span><input name="county" defaultValue={editingProperty?.county ?? ""} /></label>
                <label className="form-field"><span>ZIP code</span><input name="zip_code" defaultValue={editingProperty?.zip_code ?? ""} /></label>
                <label className="form-field"><span>County FIPS (5 digits)</span><input name="county_fips" inputMode="numeric" pattern="[0-9]{5}" defaultValue={editingProperty?.county_fips ?? ""} /></label>
                <label className="form-field"><span>Lead type</span><select name="source_type" defaultValue={editingProperty?.source_type ?? "conventional"}><option value="conventional">Conventional listing</option><option value="tax_sale">Tax sale</option><option value="code_enforcement">Code enforcement</option><option value="foreclosure">Foreclosure</option><option value="pre_foreclosure">Pre-foreclosure</option><option value="other">Other</option></select></label>
                <label className="form-field"><span>Source / agency</span><input name="source_name" placeholder="County assessor, listing site..." defaultValue={editingProperty?.source_name ?? ""} /></label>
                <label className="form-field wide"><span>Source URL</span><input name="source_url" type="url" placeholder="https://" defaultValue={editingProperty?.source_url ?? ""} /></label>
                <label className="form-field"><span>Latitude</span><input name="latitude" type="number" step="any" min="-90" max="90" defaultValue={editingProperty?.latitude ?? ""} /></label>
                <label className="form-field"><span>Longitude</span><input name="longitude" type="number" step="any" min="-180" max="180" defaultValue={editingProperty?.longitude ?? ""} /></label>
              </div>

              <div className="form-section-title">Acquisition &amp; operating costs</div>
              <div className="form-grid">
                <label className="form-field"><span>Asking price ($)</span><input name="asking_price" type="number" min="1" step="any" defaultValue={editingProperty?.asking_price ?? ""} /></label>
                <label className="form-field"><span>Repairs estimate ($)</span><input name="estimated_repairs" type="number" min="0" step="any" defaultValue={editingProperty?.estimated_repairs ?? ""} /></label>
                <label className="form-field"><span>Annual property tax ($)</span><input name="annual_property_tax" type="number" min="0" step="any" defaultValue={editingProperty?.annual_property_tax ?? ""} /></label>
                <label className="form-field"><span>Assessed value ($)</span><input name="assessed_value" type="number" min="0" step="any" defaultValue={editingProperty?.assessed_value ?? ""} /></label>
                <label className="form-field"><span>Tax rate (%)</span><input name="tax_rate_percent" type="number" min="0" max="25" step="any" placeholder="e.g. 1.2" defaultValue={editingProperty?.tax_rate_percent ?? ""} /></label>
                <label className="form-field"><span>Annual insurance quote / estimate ($)</span><input name="annual_insurance_estimate" type="number" min="0" step="any" defaultValue={editingProperty?.annual_insurance_estimate ?? ""} /></label>
                <label className="form-field wide"><span>Insurance provider or assumption source</span><input name="insurance_source" placeholder="Insurer, date, or user assumption" defaultValue={editingProperty?.insurance_source ?? editingProperty?.source_metadata.insurance?.source_name ?? ""} /></label>
                <label className="form-field wide"><span>Insurance source URL</span><input name="insurance_source_url" type="url" placeholder="https://" defaultValue={editingProperty?.source_metadata.insurance?.source_url ?? ""} /></label>
                <label className="form-field"><span>Bedrooms</span><input name="bedrooms" type="number" min="0" max="30" defaultValue={editingProperty?.bedrooms ?? ""} /></label>
                <label className="form-field"><span>Bathrooms</span><input name="bathrooms" type="number" min="0" max="30" step="0.5" defaultValue={editingProperty?.bathrooms ?? ""} /></label>
                <label className="form-field"><span>Square feet</span><input name="square_feet" type="number" min="0" defaultValue={editingProperty?.square_feet ?? ""} /></label>
                <label className="form-field"><span>Year built</span><input name="year_built" type="number" min="1600" max="2200" defaultValue={editingProperty?.year_built ?? ""} /></label>
              </div>

              <div className="form-section-title">Rent, housing agency &amp; market signals</div>
              <div className="form-grid">
                <label className="form-field"><span>Market rent / month ($)</span><input name="expected_market_rent_monthly" type="number" min="0" step="any" defaultValue={editingProperty?.expected_market_rent_monthly ?? ""} /></label>
                <label className="form-field"><span>HUD Fair Market Rent / month ($)</span><input name="hud_fmr_monthly" type="number" min="0" step="any" defaultValue={editingProperty?.hud_fmr_monthly ?? ""} /></label>
                <label className="form-field"><span>PHA payment standard / month ($)</span><input name="pha_payment_standard_monthly" type="number" min="0" step="any" defaultValue={editingProperty?.pha_payment_standard_monthly ?? ""} /></label>
                <label className="form-field"><span>Housing agency / PHA</span><input name="pha_name" defaultValue={editingProperty?.pha_name ?? ""} /></label>
                <label className="form-field"><span>PHA ID</span><input name="pha_id" defaultValue={editingProperty?.pha_id ?? ""} /></label>
                <label className="form-field"><span>Voucher program</span><select name="pha_program_status" defaultValue={editingProperty?.pha_program_status ?? "unknown"}><option value="unknown">Not verified</option><option value="confirmed">Confirmed</option><option value="not_found">Not found</option></select></label>
                <label className="form-field"><span>Waitlist status</span><select name="voucher_waitlist_status" defaultValue={editingProperty?.voucher_waitlist_status ?? "unknown"}><option value="unknown">Unknown / not published</option><option value="open">Open</option><option value="closed">Closed</option></select></label>
                <label className="form-field"><span>Open voucher count</span><input name="open_voucher_count" type="number" min="0" defaultValue={editingProperty?.open_voucher_count ?? ""} /></label>
                <label className="form-field"><span>Population growth (%)</span><input name="population_growth_percent" type="number" step="any" defaultValue={editingProperty?.population_growth_percent ?? ""} /></label>
                <label className="form-field"><span>Violent crime rate / 100k</span><input name="violent_crime_rate_per_100k" type="number" min="0" step="any" defaultValue={editingProperty?.violent_crime_rate_per_100k ?? ""} /></label>
              </div>
              <div className="form-section-title">Sources for supporting figures</div>
              <div className="form-grid">
                <label className="form-field"><span>Property tax source</span><input name="tax_source_name" placeholder="County assessor, tax bill..." defaultValue={editingProperty?.source_metadata.tax?.source_name ?? ""} /></label>
                <label className="form-field"><span>Tax source URL</span><input name="tax_source_url" type="url" placeholder="https://" defaultValue={editingProperty?.source_metadata.tax?.source_url ?? ""} /></label>
                <label className="form-field"><span>Market rent source</span><input name="market_rent_source_name" placeholder="Rental comps, provider..." defaultValue={editingProperty?.source_metadata.market_rent?.source_name ?? ""} /></label>
                <label className="form-field"><span>Market rent source URL</span><input name="market_rent_source_url" type="url" placeholder="https://" defaultValue={editingProperty?.source_metadata.market_rent?.source_url ?? ""} /></label>
                <label className="form-field"><span>HUD FMR source</span><input name="hud_source_name" placeholder="HUD dataset / vintage..." defaultValue={editingProperty?.source_metadata.hud_fmr?.source_name ?? ""} /></label>
                <label className="form-field"><span>HUD source URL</span><input name="hud_source_url" type="url" placeholder="https://" defaultValue={editingProperty?.source_metadata.hud_fmr?.source_url ?? ""} /></label>
                <label className="form-field"><span>PHA source</span><input name="pha_source_name" placeholder="Housing agency / publication..." defaultValue={editingProperty?.source_metadata.pha?.source_name ?? ""} /></label>
                <label className="form-field"><span>PHA source URL</span><input name="pha_source_url" type="url" placeholder="https://" defaultValue={editingProperty?.source_metadata.pha?.source_url ?? ""} /></label>
                <label className="form-field"><span>Neighborhood data source</span><input name="neighborhood_source_name" placeholder="Census, crime data..." defaultValue={editingProperty?.source_metadata.neighborhood?.source_name ?? ""} /></label>
                <label className="form-field"><span>Neighborhood source URL</span><input name="neighborhood_source_url" type="url" placeholder="https://" defaultValue={editingProperty?.source_metadata.neighborhood?.source_url ?? ""} /></label>
              </div>
              <div className="form-help">A voucher count is not inferred from a waitlist status. Census enrichment can be requested after saving when a valid county FIPS is present.</div>

              <div className="modal-actions">
                <button type="button" className="button button-outline" onClick={() => setShowForm(false)}>Cancel</button>
                <button type="submit" className="button button-primary" disabled={saving}>{saving ? "Saving..." : editingProperty ? "Save changes" : "Save opportunity"}</button>
              </div>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}

export default App;
