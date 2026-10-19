export type Property = {
  id: number;
  address: string;
  city: string;
  state: string;
  zip_code: string | null;
  county: string | null;
  county_fips: string | null;
  latitude: number | null;
  longitude: number | null;
  source_type: "conventional" | "tax_sale" | "code_enforcement" | "other";
  source_name: string | null;
  source_url: string | null;
  asking_price: number | null;
  estimated_repairs: number | null;
  bedrooms: number | null;
  bathrooms: number | null;
  square_feet: number | null;
  year_built: number | null;
  annual_property_tax: number | null;
  assessed_value: number | null;
  tax_rate_percent: number | null;
  annual_insurance_estimate: number | null;
  insurance_source: string | null;
  expected_market_rent_monthly: number | null;
  hud_fmr_monthly: number | null;
  pha_payment_standard_monthly: number | null;
  pha_name: string | null;
  pha_id: string | null;
  pha_program_status: "confirmed" | "not_found" | "unknown";
  voucher_waitlist_status: "open" | "closed" | "unknown";
  open_voucher_count: number | null;
  population_current: number | null;
  population_previous: number | null;
  population_growth_percent: number | null;
  population_data_year: number | null;
  violent_crime_rate_per_100k: number | null;
  created_at: string;
  updated_at: string;
  evidence: Evidence[];
};

export type Evidence = {
  id: number;
  metric: string;
  value: string;
  source_name: string;
  source_url: string | null;
  confidence: string;
  observed_at: string;
};

export type DataSource = {
  id: string;
  name: string;
  category: string;
  availability: string;
  access: string;
  url: string | null;
};

export type Scenario = {
  rent_monthly: number | null;
  rent_basis: string;
  annual_property_tax: number | null;
  property_tax_method: string | null;
  annual_insurance: number | null;
  monthly_costs: Record<string, number | null>;
  monthly_operating_cash_flow_before_financing_and_hoa: number | null;
  annual_noi_before_financing_and_hoa: number | null;
  cap_rate_percent_before_financing_and_hoa: number | null;
  missing_inputs: string[];
  complete_for_displayed_costs: boolean;
  excludes: string[];
};

export type Underwriting = {
  property_id: number;
  property_tax_annual: number | null;
  property_tax_method: string | null;
  insurance_annual: number | null;
  market_rent_scenario: Scenario;
  section8: {
    pha_name: string | null;
    pha_id: string | null;
    program_status: string;
    waitlist_status: string;
    open_voucher_count: number | null;
    voucher_count_note: string;
    hud_fmr_monthly: number | null;
    pha_payment_standard_monthly: number | null;
    published_rent_benchmark_monthly: number | null;
    benchmark_basis: string;
    rent_is_estimate_not_approval: boolean;
    scenario: Scenario;
  };
  score: {
    overall: number | null;
    coverage: number;
    components: Record<string, number>;
    weights: Record<string, number>;
    formula_notes: Record<string, string>;
  };
  assumptions: {
    vacancy_rate_percent: number;
    maintenance_rate_percent: number;
    management_rate_percent: number;
    yield_weight: number;
    growth_weight: number;
    safety_weight: number;
  };
};

export type PortfolioSummary = {
  property_count: number;
  states: Record<string, number>;
  lead_types: Record<string, number>;
  insurance_missing: number;
  voucher_counts_unknown: number;
};

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null);
    const detail =
      body && typeof body === "object" && "detail" in body
        ? JSON.stringify(body.detail)
        : `${response.status} ${response.statusText}`;
    throw new Error(detail);
  }
  return (await response.json()) as T;
}

export const api = {
  properties: () => request<Property[]>("/api/properties?limit=1000"),
  dataSources: () => request<DataSource[]>("/api/data-sources"),
  summary: () => request<PortfolioSummary>("/api/portfolio/summary"),
  createProperty: (payload: Record<string, unknown>) =>
    request<Property>("/api/properties", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  importCsv: (csv: string) =>
    request<{ imported: number; property_ids: number[] }>("/api/properties/import", {
      method: "POST",
      headers: { "Content-Type": "text/csv" },
      body: csv,
    }),
  underwriting: (id: number) =>
    request<Underwriting>(`/api/properties/${id}/underwriting`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    }),
  census: (id: number) =>
    request<Property>(`/api/properties/${id}/enrich/census`, {
      method: "POST",
    }),
};
