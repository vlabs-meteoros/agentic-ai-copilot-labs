// Tests for the JavaScript port of kavericlaims/policy.py (Lab 16).
// Run from the kavericlaims folder:  node --test js/policy.test.js
//
// policy_cases.json is generated from the Python code, and tests/test_policy_cases.py checks it against Python,
// so the JavaScript and the Python version must give exactly the same answers.
const test = require("node:test");
const assert = require("node:assert/strict");
const cases = require("./policy_cases.json");
const { getTier, getLimit, needsReceipt, NO_LIMIT } = require("./policy.js");

test("getTier: tier 1 cities, tier 2 cities and overseas claims", () => {
  for (const c of cases.get_tier) {
    assert.equal(getTier(c.city, c.currency), c.expected, `getTier("${c.city}", "${c.currency}")`);
  }
});

test("getLimit: every category, grade and tier", () => {
  for (const c of cases.get_limit) {
    assert.equal(getLimit(c.category, c.grade, c.tier), c.expected, `getLimit("${c.category}", "${c.grade}", ${c.tier})`);
  }
});

test("needsReceipt: 500.00 or more needs a receipt", () => {
  for (const c of cases.needs_receipt) {
    assert.equal(needsReceipt(c.amount), c.expected, `needsReceipt(${c.amount})`);
  }
});

test("NO_LIMIT is exported and is what TRAVEL returns", () => {
  assert.equal(NO_LIMIT, -1);
  assert.equal(getLimit("TRAVEL", "G1", 1), NO_LIMIT);
});
