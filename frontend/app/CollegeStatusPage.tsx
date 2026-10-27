"use client";

import { useMemo, useState } from "react";

type FdrStatus = "Active" | "Renewal due" | "Under review";
type College = {
  id: string;
  name: string;
  city: string;
  state: string;
  x: number;
  y: number;
  status: FdrStatus;
  maturity: string;
  history: number;
};

const colleges: College[] = [
  { id: "iitb", name: "Dwarkadas J Sanghvi College of Engineering", city: "Mumbai", state: "Maharashtra", x: 292, y: 361, status: "Active", maturity: "18 Sep 2027", history: 0 },
  { id: "coep", name: "COEP Technological University", city: "Pune", state: "Maharashtra", x: 310, y: 350, status: "Renewal due", maturity: "14 Dec 2026", history: 1 },
  { id: "ict", name: "Institute of Chemical Technology", city: "Mumbai", state: "Maharashtra", x: 282, y: 373, status: "Under review", maturity: "02 Nov 2026", history: 2 },
  { id: "iitd", name: "IIT Delhi", city: "New Delhi", state: "Delhi", x: 350, y: 178, status: "Active", maturity: "21 Jun 2027", history: 0 },
  { id: "dtu", name: "Delhi Technological University", city: "Delhi", state: "Delhi", x: 362, y: 170, status: "Renewal due", maturity: "09 Jan 2027", history: 1 },
  { id: "nsut", name: "Netaji Subhas University of Technology", city: "Delhi", state: "Delhi", x: 342, y: 190, status: "Active", maturity: "30 Aug 2027", history: 0 },
  { id: "iisc", name: "Indian Institute of Science", city: "Bengaluru", state: "Karnataka", x: 328, y: 441, status: "Active", maturity: "11 May 2027", history: 0 },
  { id: "nitk", name: "NIT Karnataka", city: "Surathkal", state: "Karnataka", x: 299, y: 414, status: "Under review", maturity: "22 Oct 2026", history: 1 },
  { id: "rvce", name: "R.V. College of Engineering", city: "Bengaluru", state: "Karnataka", x: 340, y: 450, status: "Renewal due", maturity: "28 Feb 2027", history: 0 },
  { id: "iitm", name: "IIT Madras", city: "Chennai", state: "Tamil Nadu", x: 385, y: 454, status: "Active", maturity: "16 Jul 2027", history: 0 },
  { id: "anna", name: "Anna University", city: "Chennai", state: "Tamil Nadu", x: 397, y: 444, status: "Renewal due", maturity: "19 Jan 2027", history: 1 },
  { id: "nitt", name: "NIT Tiruchirappalli", city: "Tiruchirappalli", state: "Tamil Nadu", x: 405, y: 474, status: "Active", maturity: "04 Oct 2027", history: 0 },
  { id: "iith", name: "IIT Hyderabad", city: "Sangareddy", state: "Telangana", x: 352, y: 363, status: "Under review", maturity: "12 Nov 2026", history: 2 },
  { id: "osmania", name: "Osmania University", city: "Hyderabad", state: "Telangana", x: 367, y: 373, status: "Active", maturity: "24 Apr 2027", history: 0 },
  { id: "jntuh", name: "JNTU Hyderabad", city: "Hyderabad", state: "Telangana", x: 360, y: 382, status: "Renewal due", maturity: "06 Mar 2027", history: 1 },
  { id: "iitkgp", name: "IIT Kharagpur", city: "Kharagpur", state: "West Bengal", x: 494, y: 260, status: "Active", maturity: "17 Dec 2027", history: 0 },
  { id: "jadavpur", name: "Jadavpur University", city: "Kolkata", state: "West Bengal", x: 514, y: 271, status: "Under review", maturity: "03 Nov 2026", history: 1 },
  { id: "iiest", name: "IIEST Shibpur", city: "Howrah", state: "West Bengal", x: 505, y: 282, status: "Active", maturity: "08 Aug 2027", history: 0 },
  { id: "iitgn", name: "IIT Gandhinagar", city: "Gandhinagar", state: "Gujarat", x: 210, y: 292, status: "Renewal due", maturity: "15 Feb 2027", history: 1 },
  { id: "ldce", name: "L.D. College of Engineering", city: "Ahmedabad", state: "Gujarat", x: 198, y: 303, status: "Active", maturity: "27 May 2027", history: 0 },
  { id: "svnit", name: "SVNIT Surat", city: "Surat", state: "Gujarat", x: 218, y: 322, status: "Under review", maturity: "01 Nov 2026", history: 2 },
  { id: "iitk", name: "IIT Kanpur", city: "Kanpur", state: "Uttar Pradesh", x: 387, y: 235, status: "Active", maturity: "09 Sep 2027", history: 0 },
  { id: "bhu", name: "Banaras Hindu University", city: "Varanasi", state: "Uttar Pradesh", x: 420, y: 252, status: "Renewal due", maturity: "21 Jan 2027", history: 1 },
  { id: "mnnit", name: "MNNIT Allahabad", city: "Prayagraj", state: "Uttar Pradesh", x: 405, y: 244, status: "Active", maturity: "13 Jun 2027", history: 0 },
];

const statusClass: Record<FdrStatus, string> = {
  Active: "active",
  "Renewal due": "renewal",
  "Under review": "review",
};

const mapLabels = [
  { name: "MAHARASHTRA", x: 250, y: 395 },
  { name: "DELHI", x: 326, y: 148 },
  { name: "KARNATAKA", x: 277, y: 467 },
  { name: "TAMIL NADU", x: 414, y: 511 },
  { name: "TELANGANA", x: 350, y: 404 },
  { name: "WEST BENGAL", x: 507, y: 309 },
  { name: "GUJARAT", x: 151, y: 323 },
  { name: "UTTAR PRADESH", x: 414, y: 215 },
];

function statusCounts(items: College[]) {
  return items.reduce(
    (counts, item) => ({ ...counts, [item.status]: counts[item.status] + 1 }),
    { Active: 0, "Renewal due": 0, "Under review": 0 },
  );
}

export default function CollegeStatusPage() {
  const [query, setQuery] = useState("");
  const [stateFilter, setStateFilter] = useState("All states");
  const [statusFilter, setStatusFilter] = useState("All statuses");
  const [selectedId, setSelectedId] = useState("iitb");
  const [zoom, setZoom] = useState(1);
  const [is3d, setIs3d] = useState(true);

  const visible = useMemo(() => colleges.filter((college) => {
    const matchesQuery = `${college.name} ${college.city} ${college.state}`.toLowerCase().includes(query.toLowerCase());
    return matchesQuery
      && (stateFilter === "All states" || college.state === stateFilter)
      && (statusFilter === "All statuses" || college.status === statusFilter);
  }), [query, stateFilter, statusFilter]);
  const selected = visible.find((college) => college.id === selectedId) || visible[0];
  const counts = statusCounts(visible);
  const states = Array.from(new Set(colleges.map((college) => college.state)));
  const visibleIds = new Set(visible.map((college) => college.id));

  function chooseStatus(status: string) {
    setStatusFilter(statusFilter === status ? "All statuses" : status);
  }

  return (
    <div className="college-status">
      <div className="college-status-note"><span>ⓘ</span><p> College status information.</p></div>

      <div className="college-kpis">
        <button className={`college-kpi total ${statusFilter === "All statuses" ? "chosen" : ""}`} onClick={() => setStatusFilter("All statuses")}><span>Institutions in view</span><strong>{visible.length}</strong><small>Across {new Set(visible.map((college) => college.state)).size} states</small><i>⌖</i></button>
        <button className={`college-kpi good ${statusFilter === "Active" ? "chosen" : ""}`} onClick={() => chooseStatus("Active")}><span>FDR active</span><strong>{counts.Active}</strong><small>Demo record in order</small><i>✓</i></button>
        <button className={`college-kpi caution ${statusFilter === "Renewal due" ? "chosen" : ""}`} onClick={() => chooseStatus("Renewal due")}><span>Renewal due</span><strong>{counts["Renewal due"]}</strong><small>Sample follow-up needed</small><i>↻</i></button>
        <button className={`college-kpi attention ${statusFilter === "Under review" ? "chosen" : ""}`} onClick={() => chooseStatus("Under review")}><span>Under review</span><strong>{counts["Under review"]}</strong><small>Sample officer review</small><i>◎</i></button>
      </div>

      <section className="college-panel map-panel">
        <div className="college-panel-head">
          <div><span className="college-kicker">NATIONAL VIEW · LIVE FILTERS</span><h2>College status across India</h2><p>Explore the sample FDR portfolio by region. Select a glowing marker to inspect a college.</p></div>
          <div className="map-legend"><span><i className="legend-dot active" />Active</span><span><i className="legend-dot renewal" />Renewal due</span><span><i className="legend-dot review" />Under review</span></div>
        </div>
        <div className="map-controls">
          <label className="map-search"><span>⌕</span><input aria-label="Search colleges or cities" placeholder="Search college or city" value={query} onChange={(event) => setQuery(event.target.value)} /></label>
          <select aria-label="Filter by state" value={stateFilter} onChange={(event) => setStateFilter(event.target.value)}><option>All states</option>{states.map((state) => <option key={state}>{state}</option>)}</select>
          <div className="zoom-controls"><button aria-label="Zoom out" onClick={() => setZoom(Math.max(0.85, Number((zoom - 0.1).toFixed(1))))}>−</button><span>{Math.round(zoom * 100)}%</span><button aria-label="Zoom in" onClick={() => setZoom(Math.min(1.35, Number((zoom + 0.1).toFixed(1))))}>＋</button><button aria-label="Reset map zoom" onClick={() => setZoom(1)}>Reset</button></div>
          <button className={`map-view-toggle ${is3d ? "on" : ""}`} aria-pressed={is3d} onClick={() => setIs3d(!is3d)}><span>◇</span>{is3d ? "3D view" : "Flat view"}</button>
        </div>
        <div className={`college-map ${is3d ? "is-3d" : ""}`}>
          <svg className="india-map-svg" viewBox="0 0 720 560" role="img" aria-label="Illustrative map of India with interactive college FDR status markers">
            <defs>
              <linearGradient id="indiaFill" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#e9f4f2" /><stop offset="1" stopColor="#d7e9e9" /></linearGradient>
              <filter id="markerGlow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3" result="blur" /><feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
            </defs>
            <g className="map-grid">{Array.from({ length: 10 }, (_, index) => <line key={`v${index}`} x1={80 + index * 62} y1="54" x2={80 + index * 62} y2="518" />)}{Array.from({ length: 8 }, (_, index) => <line key={`h${index}`} x1="70" y1={75 + index * 58} x2="670" y2={75 + index * 58} />)}</g>
            <g transform={`translate(${360 - 360 * zoom} ${280 - 280 * zoom}) scale(${zoom})`}>
              <path className="india-land" d="M259 70 L285 79 L300 96 L328 98 L348 113 L376 105 L398 119 L422 119 L437 137 L461 141 L476 158 L495 168 L517 189 L535 205 L532 220 L548 236 L539 249 L555 262 L542 279 L529 283 L521 302 L508 311 L500 332 L481 348 L469 367 L459 388 L443 402 L434 424 L417 446 L405 470 L389 486 L380 469 L367 447 L356 428 L347 410 L334 397 L321 379 L308 366 L293 350 L278 338 L263 324 L245 315 L230 302 L210 295 L195 278 L176 270 L163 256 L148 251 L138 232 L148 213 L160 198 L170 180 L184 169 L193 151 L210 144 L222 130 L235 117 L241 99 Z" />
              <path className="india-coast" d="M259 70 L285 79 L300 96 L328 98 L348 113 L376 105 L398 119 L422 119 L437 137 L461 141 L476 158 L495 168 L517 189 L535 205 L532 220 L548 236 L539 249 L555 262 L542 279 L529 283 L521 302 L508 311 L500 332 L481 348 L469 367 L459 388 L443 402 L434 424 L417 446 L405 470 L389 486 L380 469 L367 447 L356 428 L347 410 L334 397 L321 379 L308 366 L293 350 L278 338 L263 324 L245 315 L230 302 L210 295 L195 278 L176 270 L163 256 L148 251 L138 232 L148 213 L160 198 L170 180 L184 169 L193 151 L210 144 L222 130 L235 117 L241 99 Z" />
              {mapLabels.map((label) => <text className="map-state-label" key={label.name} x={label.x} y={label.y}>{label.name}</text>)}
              {visible.map((college) => <g className={`map-marker ${statusClass[college.status]} ${selected?.id === college.id ? "selected" : ""}`} key={college.id} role="button" tabIndex={0} aria-label={`${college.name}, ${college.status}${college.history ? `, ${college.history} sample history flags` : ""}`} onClick={() => setSelectedId(college.id)} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setSelectedId(college.id); } }} transform={`translate(${college.x} ${college.y})`}>
                <circle className="marker-pulse" r="13" /><circle className="marker-core" r="7" /><circle className="marker-center" r="2.5" />
                {college.history > 0 && <g className="marker-flag" transform="translate(9 -11)"><circle r="7" /><text y="3">!</text></g>}
                <title>{college.name} · {college.city} · {college.status}</title>
              </g>)}
            </g>
            <g className="map-compass" transform="translate(635 75)"><circle r="24" /><path d="M0 -15 L5 3 L0 0 L-5 3 Z" /><text y="39">N</text></g>
          </svg>
          {selected && <div className="map-selected-card"><div className={`college-crest ${statusClass[selected.status]}`}>✦</div><div className="map-selected-copy"><strong>{selected.name}</strong><span>{selected.city}, {selected.state}</span></div><span className={`college-status-pill ${statusClass[selected.status]}`}>{selected.status}</span><button aria-label="View college details" onClick={() => document.getElementById("selected-college")?.scrollIntoView({ behavior: "smooth", block: "center" })}>↗</button></div>}
          {visible.length === 0 && <div className="map-empty">No colleges match these filters. Try another state or search term.</div>}
        </div>
        <div className="map-footer"><span><i className="live-pulse" /> DEMO PORTFOLIO · {visible.length} INSTITUTIONS</span><span>Marker size is fixed · select a marker for details</span></div>
      </section>

      <section className="college-panel network-panel">
        <div className="college-panel-head network-heading">
          <div><span className="college-kicker">RELATIONSHIP EXPLORER · SAMPLE HISTORY</span><h2>Institution network</h2><p>Connected colleges share a state. Select any node to review its sample status and history flags.</p></div>
          <div className="network-key"><span><i className="key-node active" />Active</span><span><i className="key-node renewal" />Renewal due</span><span><i className="key-node review" />Under review</span><span><b>⚑</b>Sample policy-history flag</span></div>
        </div>
        <div className="network-layout">
          <div className="network-canvas">
            <svg viewBox="0 0 900 410" role="img" aria-label="Interactive college network graph with edges connecting colleges in the same state">
              <defs><filter id="nodeGlow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="4" result="blur" /><feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge></filter></defs>
              <g className="network-edge">{states.map((state) => {
                const group = visible.filter((college) => college.state === state);
                return group.slice(1).map((college, index) => <line key={`${state}-${college.id}`} x1={networkPosition(group[0], state).x} y1={networkPosition(group[0], state).y} x2={networkPosition(college, state).x} y2={networkPosition(college, state).y} className={visibleIds.has(selected?.id || "") && group.some((item) => item.id === selected?.id) ? "related" : ""} />);
              })}</g>
              {visible.map((college) => {
                const point = networkPosition(college, college.state);
                return <g className={`network-node ${statusClass[college.status]} ${selected?.id === college.id ? "selected" : ""}`} key={college.id} transform={`translate(${point.x} ${point.y})`} role="button" tabIndex={0} aria-label={`Select ${college.name}`} onClick={() => { setSelectedId(college.id); }} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setSelectedId(college.id); } }}>
                  <circle className="node-halo" r="16" /><circle className="node-dot" r="9" />
                  {college.history > 0 && <g className="node-flag" transform="translate(12 -12)"><circle r="7" /><text y="3">!</text></g>}
                  <text className="node-label" y="27">{shortName(college.name)}</text>
                  <text className="node-state" y="40">{college.state}</text>
                </g>;
              })}
            </svg>
            {visible.length === 0 && <div className="network-empty">No institutions to display.</div>}
          </div>
          {selected && <aside id="selected-college" className="college-detail">
            <div className="detail-topline"><span>SELECTED INSTITUTION</span><span className={`college-status-pill ${statusClass[selected.status]}`}>{selected.status}</span></div>
            <div className="detail-title"><div className={`college-crest ${statusClass[selected.status]}`}>✦</div><div><h3>{selected.name}</h3><span>{selected.city}, {selected.state}</span></div></div>
            <div className="detail-fdr"><div><span>FDR RECORD</span><strong><i className={`legend-dot ${statusClass[selected.status]}`} />{selected.status}</strong></div><div><span>MATURITY DATE</span><strong>{selected.maturity}</strong></div></div>
            <div className={`history-box ${selected.history ? "has-history" : ""}`}><span className="history-icon">{selected.history ? "⚑" : "✓"}</span><div><strong>{selected.history ? `${selected.history} sample history flag${selected.history > 1 ? "s" : ""}` : "No sample history flags"}</strong><p>{selected.history ? "Illustrative policy-review history only. Not a real allegation, finding, or enforcement record." : "This demo record has no illustrative policy-review history."}</p></div></div>
            <span className="demo-record-label">FOR AICTE RECORD</span>
          </aside>}
        </div>
        <div className="network-footnote"><span>Showing {visible.length} of {colleges.length} sample institutions</span><span>Edges indicate shared state only — not a risk or compliance relationship.</span></div>
      </section>
    </div>
  );
}

function networkPosition(college: College, state: string) {
  const groups = Array.from(new Set(colleges.map((item) => item.state)));
  const groupIndex = groups.indexOf(state);
  const row = Math.floor(groupIndex / 4);
  const column = groupIndex % 4;
  const inState = colleges.filter((item) => item.state === state);
  const localIndex = inState.findIndex((item) => item.id === college.id);
  const localOffsets = [[0, 0], [-32, 46], [34, 46]];
  const offset = localOffsets[localIndex] || [0, 0];
  return { x: 120 + column * 220 + offset[0], y: 100 + row * 180 + offset[1] };
}

function shortName(name: string) {
  const abbreviations: Record<string, string> = {
    "COEP Technological University": "COEP",
    "Institute of Chemical Technology": "ICT Mumbai",
    "Delhi Technological University": "DTU",
    "Netaji Subhas University of Technology": "NSUT",
    "Indian Institute of Science": "IISc",
    "NIT Karnataka": "NITK",
    "R.V. College of Engineering": "RVCE",
    "NIT Tiruchirappalli": "NIT Trichy",
    "Anna University": "Anna University",
    "Osmania University": "Osmania",
    "JNTU Hyderabad": "JNTUH",
    "Jadavpur University": "Jadavpur",
    "IIEST Shibpur": "IIEST",
    "L.D. College of Engineering": "LDCE",
    "Banaras Hindu University": "BHU",
    "MNNIT Allahabad": "MNNIT",
  };
  return abbreviations[name] || name;
}
