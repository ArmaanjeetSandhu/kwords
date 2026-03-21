let DATA = [];

const state = { contig: "both", order: "all", rel: "both", joeys: "all" };

function setFilter(group, val, btn) {
  state[group] = val;
  btn
    .closest(".filter-group")
    .querySelectorAll(".seg-btn")
    .forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  render();
}

function findAllPaths(parentStr, joeyStr) {
  const p = parentStr.toUpperCase();
  const j = joeyStr.toUpperCase();
  const paths = [];

  function search(jIdx, currentPath, usedIndices) {
    if (jIdx === j.length) {
      paths.push([...currentPath]);
      return;
    }
    const charTarget = j[jIdx];
    for (let i = 0; i < p.length; i++) {
      if (p[i] === charTarget && !usedIndices.has(i)) {
        usedIndices.add(i);
        currentPath.push(i);
        search(jIdx + 1, currentPath, usedIndices);
        currentPath.pop();
        usedIndices.delete(i);
      }
    }
  }

  search(0, [], new Set());

  const uniquePaths = [];
  const seen = new Set();
  for (const path of paths) {
    const key = path.join(",");
    if (!seen.has(key)) {
      seen.add(key);
      uniquePaths.push(path);
    }
  }
  return uniquePaths;
}

function getPathProperties(path) {
  let isOrdered = true;
  let isReverse = true;
  let isContiguous = true;

  for (let i = 1; i < path.length; i++) {
    if (path[i] <= path[i - 1]) isOrdered = false;
    if (path[i] >= path[i - 1]) isReverse = false;
    if (Math.abs(path[i] - path[i - 1]) !== 1) isContiguous = false;
  }

  let order = "unordered";
  if (isOrdered) order = "ordered";
  else if (isReverse) order = "reverse";

  return { contig: isContiguous, order: order };
}

function highlightHTML(parent, path) {
  const hi = new Set(path);
  return parent
    .split("")
    .map(
      (ch, i) =>
        `<span class="${hi.has(i) ? "letter-hi" : "letter-dim"}">${ch}</span>`,
    )
    .join("");
}

function badgeHTML(props, rel) {
  return [
    `<span class="badge ${props.contig ? "b-contig" : "b-noncontig"}">${props.contig ? "contiguous" : "non-contiguous"}</span>`,
    `<span class="badge ${props.order === "ordered" ? "b-ordered" : props.order === "reverse" ? "b-reverse" : "b-unordered"}">${props.order === "ordered" ? "sorted ↑" : props.order === "reverse" ? "reverse ↓" : "unordered"}</span>`,
    `<span class="badge ${rel === "synonym" ? "b-syn" : "b-ant"}">${rel}</span>`,
  ].join("");
}

function render() {
  const results = [];
  let totalJoeys = 0;
  let totalFormations = 0;

  for (const e of DATA) {
    const matchedJoeys = [];

    for (const j of e.joeys) {
      if (state.rel !== "both" && j.rel !== state.rel) continue;

      const paths = findAllPaths(e.parent, j.word);
      const uniqueFormations = new Map();

      for (const path of paths) {
        const props = getPathProperties(path);

        if (state.contig === "contiguous" && !props.contig) continue;
        if (state.contig === "noncontiguous" && props.contig) continue;
        if (state.order !== "all" && props.order !== state.order) continue;

        const badgeKey = `${props.contig}-${props.order}`;
        if (!uniqueFormations.has(badgeKey))
          uniqueFormations.set(badgeKey, { path, props });
      }

      const matchedPaths = Array.from(uniqueFormations.values());

      if (matchedPaths.length > 0) {
        matchedJoeys.push({ ...j, matchedPaths });
        totalFormations += matchedPaths.length;
      }
    }

    if (matchedJoeys.length > 0) {
      if (state.joeys === "one" && matchedJoeys.length !== 1) continue;
      if (state.joeys === "two" && matchedJoeys.length < 2) continue;

      results.push({ parent: e.parent, joeys: matchedJoeys });
      totalJoeys += matchedJoeys.length;
    }
  }

  document.getElementById("stats").innerHTML =
    `Showing <strong>${results.length}</strong> parent ${results.length === 1 ? "word" : "words"} &mdash; <strong>${totalJoeys}</strong> ${totalJoeys === 1 ? "joey" : "joeys"} &mdash; <strong>${totalFormations}</strong> distinct valid ${totalFormations === 1 ? "formation" : "formations"}`;

  const grid = document.getElementById("grid");
  if (!results.length) {
    grid.innerHTML =
      '<div class="empty">No words match the current filters.</div>';
    return;
  }

  grid.innerHTML = results
    .map((e, ei) => {
      const joeysHTML = e.joeys
        .map((j, ji) => {
          return j.matchedPaths
            .map((formation, fi) => {
              const hiHTML = highlightHTML(e.parent, formation.path);

              const isMultiJoey = e.joeys.length > 1;
              const isMultiVar = j.matchedPaths.length > 1;
              let label = "";
              if (isMultiJoey && isMultiVar)
                label = `Joey ${ji + 1} (Var ${fi + 1})`;
              else if (isMultiJoey) label = `Joey ${ji + 1}`;
              else if (isMultiVar) label = `Variant ${fi + 1}`;

              return `
        <div class="joey-block">
          <div class="joey-word-row">
            <span class="joey-word">${j.word}</span>
            ${label ? `<span class="joey-num">${label}</span>` : ""}
          </div>
          <div class="parent-highlighted">${hiHTML}</div>
          <div class="badges">${badgeHTML(formation.props, j.rel)}</div>
        </div>`;
            })
            .join('<div class="sep"></div>');
        })
        .join('<div class="sep"></div>');

      return `<div class="card" style="animation-delay:${ei * 0.03}s">
      <div class="parent-word">${e.parent}</div>
      ${joeysHTML}
    </div>`;
    })
    .join("");
}

async function initApp() {
  try {
    const response = await fetch("data.json");

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    DATA = await response.json();

    render();
  } catch (error) {
    console.error("Could not load the kangaroo words data:", error);
    document.getElementById("grid").innerHTML =
      `<div class="empty">Error loading data. Make sure you are running a local development server!</div>`;
  }
}

initApp();
