const { buildRequestConfig, formatSummaryLine } = require("./logic");

test("new expense builds a POST request", () => {
  const result = buildRequestConfig("", "http://127.0.0.1:5000");
  expect(result.method).toBe("POST");
  expect(result.url).toBe("http://127.0.0.1:5000/expenses");
});

test("editing an expense builds a PUT request with the id in the url", () => {
  const result = buildRequestConfig("7", "http://127.0.0.1:5000");
  expect(result.method).toBe("PUT");
  expect(result.url).toBe("http://127.0.0.1:5000/expenses/7");
});

test("category with no budget shows no budget info", () => {
  const line = formatSummaryLine({ category: "Transport", total: 20, budget: null, over_budget: false });
  expect(line).toBe("Transport: €20");
});

test("category under budget shows the budget with no warning", () => {
  const line = formatSummaryLine({ category: "Food", total: 20, budget: 100, over_budget: false });
  expect(line).toBe("Food: €20 (budget: €100)");
});

test("category over budget includes the warning", () => {
  const line = formatSummaryLine({ category: "Food", total: 120, budget: 100, over_budget: true });
  expect(line).toBe("Food: €120 (budget: €100) — OVER BUDGET");
});