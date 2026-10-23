from .models import Property
from .schemas import UnderwritingAssumptions


def _annual_tax_estimate(property_record: Property) -> tuple[float | None, str | None]:
    if property_record.annual_property_tax is not None:
        return property_record.annual_property_tax, "provided annual property tax"
    if property_record.assessed_value is not None and property_record.tax_rate_percent is not None:
        return (
            property_record.assessed_value * property_record.tax_rate_percent / 100,
            "assessed value multiplied by user-provided tax rate",
        )
    return None, None


def _scenario(rent: float | None, rent_basis: str, property_record: Property, assumptions):
    annual_tax, tax_method = _annual_tax_estimate(property_record)
    annual_insurance = property_record.annual_insurance_estimate
    capital_basis = None
    capital_basis_note = "asking price not supplied"
    if property_record.asking_price is not None:
        capital_basis = property_record.asking_price + (property_record.estimated_repairs or 0)
        capital_basis_note = (
            "asking price plus supplied repair estimate"
            if property_record.estimated_repairs is not None
            else "asking price only; one-time repair costs not supplied"
        )
    missing = []
    if rent is None:
        missing.append("rent benchmark")
    if annual_tax is None:
        missing.append("property tax amount or assessed value and tax rate")
    if annual_insurance is None:
        missing.append("insurance quote or user-entered estimate")

    costs = {
        "vacancy_reserve_monthly": (
            rent * assumptions.vacancy_rate_percent / 100 if rent is not None else None
        ),
        "maintenance_reserve_monthly": (
            rent * assumptions.maintenance_rate_percent / 100 if rent is not None else None
        ),
        "management_reserve_monthly": (
            rent * assumptions.management_rate_percent / 100 if rent is not None else None
        ),
        "property_tax_monthly": annual_tax / 12 if annual_tax is not None else None,
        "insurance_monthly": annual_insurance / 12 if annual_insurance is not None else None,
    }
    monthly_cash_flow = None
    annual_noi = None
    cap_rate_percent = None
    if not missing:
        monthly_cash_flow = rent - sum(costs.values())
        annual_noi = monthly_cash_flow * 12
        if capital_basis:
            cap_rate_percent = annual_noi / capital_basis * 100

    return {
        "rent_monthly": rent,
        "rent_basis": rent_basis,
        "annual_property_tax": annual_tax,
        "property_tax_method": tax_method,
        "annual_insurance": annual_insurance,
        "monthly_costs": costs,
        "monthly_operating_cash_flow_before_financing_and_hoa": monthly_cash_flow,
        "annual_noi_before_financing_and_hoa": annual_noi,
        "cap_rate_percent_before_financing_and_hoa": cap_rate_percent,
        "capital_basis_for_cap_rate": capital_basis,
        "capital_basis_note": capital_basis_note,
        "missing_inputs": missing,
        "complete_for_displayed_costs": not missing,
        "excludes": [
            "mortgage principal and interest",
            "utilities",
            "HOA or other property-specific fees",
            "closing costs; one-time repairs are included in the capital basis only when supplied",
        ],
    }


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(value, high))


def analyze_property(property_record: Property, assumptions: UnderwritingAssumptions):
    tax, tax_method = _annual_tax_estimate(property_record)
    benchmarks = [
        value
        for value in (
            property_record.hud_fmr_monthly,
            property_record.pha_payment_standard_monthly,
        )
        if value is not None
    ]
    published_benchmark = min(benchmarks) if benchmarks else None
    if property_record.hud_fmr_monthly is not None and property_record.pha_payment_standard_monthly is not None:
        benchmark_basis = "lower of HUD Fair Market Rent and published PHA payment standard"
    elif property_record.pha_payment_standard_monthly is not None:
        benchmark_basis = "published PHA payment standard only"
    elif property_record.hud_fmr_monthly is not None:
        benchmark_basis = "HUD Fair Market Rent only; PHA payment standard not supplied"
    else:
        benchmark_basis = "no published rent benchmark supplied"

    program_confirmed = property_record.pha_program_status == "confirmed"
    section8_rent = published_benchmark if program_confirmed else None
    section8_basis = benchmark_basis if program_confirmed else "PHA coverage has not been confirmed"
    market_scenario = _scenario(
        property_record.expected_market_rent_monthly,
        "user-provided market rent" if property_record.expected_market_rent_monthly is not None else "not supplied",
        property_record,
        assumptions,
    )
    section8_scenario = _scenario(
        section8_rent,
        section8_basis,
        property_record,
        assumptions,
    )

    weighted_components = {}
    weights = {
        "yield": assumptions.yield_weight,
        "population_growth": assumptions.growth_weight,
        "crime_safety": assumptions.safety_weight,
    }
    cash_flow = section8_scenario
    if cash_flow["cap_rate_percent_before_financing_and_hoa"] is None:
        cash_flow = market_scenario
    cap_rate = cash_flow["cap_rate_percent_before_financing_and_hoa"]
    if cap_rate is not None:
        weighted_components["yield"] = _clamp(cap_rate / 12 * 100, 0, 100)
    if property_record.population_growth_percent is not None:
        weighted_components["population_growth"] = _clamp(
            (property_record.population_growth_percent + 2) / 6 * 100,
            0,
            100,
        )
    if property_record.violent_crime_rate_per_100k is not None:
        weighted_components["crime_safety"] = _clamp(
            (1 - property_record.violent_crime_rate_per_100k / 5000) * 100,
            0,
            100,
        )

    usable_weight = sum(weights[name] for name in weighted_components)
    overall_score = None
    if usable_weight > 0:
        overall_score = round(
            sum(weighted_components[name] * weights[name] for name in weighted_components)
            / usable_weight,
            1,
        )

    return {
        "property_id": property_record.id,
        "property_tax_annual": tax,
        "property_tax_method": tax_method,
        "insurance_annual": property_record.annual_insurance_estimate,
        "market_rent_scenario": market_scenario,
        "section8": {
            "pha_name": property_record.pha_name,
            "pha_id": property_record.pha_id,
            "program_status": property_record.pha_program_status,
            "waitlist_status": property_record.voucher_waitlist_status,
            "open_voucher_count": property_record.open_voucher_count,
            "voucher_count_note": (
                "Count supplied by the user or source."
                if property_record.open_voucher_count is not None
                else "No public count supplied; voucher availability is unknown."
            ),
            "hud_fmr_monthly": property_record.hud_fmr_monthly,
            "pha_payment_standard_monthly": property_record.pha_payment_standard_monthly,
            "published_rent_benchmark_monthly": published_benchmark,
            "benchmark_basis": benchmark_basis,
            "rent_is_estimate_not_approval": True,
            "scenario": section8_scenario,
        },
        "score": {
            "overall": overall_score,
            "coverage": round(len(weighted_components) / len(weights), 2),
            "components": weighted_components,
            "weights": weights,
            "formula_notes": {
                "yield": "Cap rate is linearly scaled from 0% to 12%, then bounded to 0-100.",
                "population_growth": "Annual population growth is scaled from -2% to 4%, then bounded to 0-100.",
                "crime_safety": "Crime rate is scaled against 5,000 incidents per 100,000, then bounded to 0-100.",
                "overall": "Weighted average of available components only; coverage shows how many of the three inputs are present.",
            },
        },
        "assumptions": assumptions.model_dump(),
    }
