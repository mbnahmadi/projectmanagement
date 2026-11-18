(function () {
  const OPTIONS_URL = "/projects/filter-options/";

  function fillSelect(select, items, placeholder) {
    select.innerHTML = "";
    const first = document.createElement("option");
    first.value = "";
    first.textContent = placeholder;
    select.appendChild(first);

    items.forEach((item) => {
      const opt = document.createElement("option");
      opt.value = item;
      opt.textContent = item; // textContent => امن در برابر XSS
      select.appendChild(opt);
    });
  }

  async function initCascade(companyId, locationId, query = "") {
    const companySel = document.getElementById(companyId);
    const locationSel = document.getElementById(locationId);
    if (!companySel || !locationSel) return;

    let data = [];
    try {
      const res = await fetch(OPTIONS_URL + query, {
        credentials: "same-origin",
      });
      if (!res.ok) throw new Error(res.status);
      data = await res.json();
    } catch (err) {
      console.error("Failed to load filter options:", err);
      return;
    }

    const allLocations = [...new Set(data.flatMap((d) => d.locations))].sort();

    fillSelect(
      companySel,
      data.map((d) => d.company),
      "All companies",
    );
    fillSelect(locationSel, allLocations, "All locations");

    companySel.addEventListener("change", () => {
      const selected = data.find((d) => d.company === companySel.value);
      fillSelect(
        locationSel,
        selected ? selected.locations : allLocations,
        "All locations",
      );
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initCascade("company", "location");
    initCascade("company-fb", "location-fb", "?has_feedback=1");
  });
})();
