// policy.js - the expense policy rules (policy v3, April 2025): city tiers, limits and receipts.
// JavaScript port of kavericlaims/policy.py. Keep the two files in step: js/policy.test.js checks both give the same answers.

const TIER1_CITIES = new Set(["bengaluru", "chennai", "delhi", "hyderabad", "kolkata", "mumbai", "pune"]);

const NO_LIMIT = -1; // getLimit() returns this for categories without a limit
const RECEIPT_THRESHOLD = 500; // INR

// grade -> [tier 1 limit, tier 2 limit], in INR
const MEAL_LIMITS_PER_DAY = { G1: [600, 450], G2: [800, 600], G3: [1000, 800], G4: [1500, 1200] };
const HOTEL_LIMITS_PER_NIGHT = { G1: [3000, 2000], G2: [4000, 3000], G3: [6000, 4500], G4: [9000, 7000] };
const GRADE_LIMITS = { MEAL: MEAL_LIMITS_PER_DAY, HOTEL: HOTEL_LIMITS_PER_NIGHT };
const FLAT_LIMITS = { INTERNET: 1000, OTHER: 2000, TRAVEL: NO_LIMIT };

/** Return the city tier (1 or 2); foreign-currency claims are overseas and count as tier 1. */
function getTier(city, currency) {
  if (currency !== "INR" || TIER1_CITIES.has(city.toLowerCase())) {
    return 1;
  }
  return 2;
}

/** Return the INR limit for a category, grade and tier; NO_LIMIT (-1) for TRAVEL, 0 if unknown. */
function getLimit(category, grade, tier) {
  if (Object.hasOwn(FLAT_LIMITS, category)) {
    return FLAT_LIMITS[category];
  }
  const byGrade = GRADE_LIMITS[category] ?? {};
  if (!Object.hasOwn(byGrade, grade)) {
    return 0;
  }
  const [tier1Limit, tier2Limit] = byGrade[grade];
  return tier === 1 ? tier1Limit : tier2Limit;
}

/** Return true if a claim of this INR amount needs a receipt. */
function needsReceipt(amount) {
  return amount >= RECEIPT_THRESHOLD;
}

module.exports = { NO_LIMIT, RECEIPT_THRESHOLD, getTier, getLimit, needsReceipt };
