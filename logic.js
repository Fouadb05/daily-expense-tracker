function buildRequestConfig(id, apiUrl) {
  const url = id ? `${apiUrl}/expenses/${id}` : `${apiUrl}/expenses`;
  const method = id ? "PUT" : "POST";
  return { url, method };
}

function formatSummaryLine(entry) {
  let text = `${entry.category}: €${entry.total}`;

  if (entry.budget !== null) {
    text += ` (budget: €${entry.budget})`;
    if (entry.over_budget) {
      text += " — OVER BUDGET";
    }
  }

  return text;
}

module.exports = { buildRequestConfig, formatSummaryLine };