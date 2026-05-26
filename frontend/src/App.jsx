import { useEffect, useState } from "react";
import "./styles.css";

const API = "http://127.0.0.1:8000/api";

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [active, setActive] = useState("dashboard");
  const [summary, setSummary] = useState(null);
  const [records, setRecords] = useState([]);
  const [failedRows, setFailedRows] = useState([]);
  const [message, setMessage] = useState("");

  async function loginDemo() {
  setLoggedIn(true);
  await loadData();
}

  async function loadData() {
  try {
    const [s, r, f] = await Promise.all([
      fetch(`${API}/ingestion/dashboard/`).then((res) => res.json()),
      fetch(`${API}/ingestion/records/`).then((res) => res.json()),
      fetch(`${API}/ingestion/failed-rows/`).then((res) => res.json()),
    ]);

    setSummary(s);
    setRecords(r);
    setFailedRows(f);
    setMessage("");
  } catch (error) {
    setMessage("Backend not connected. Make sure Django is running on port 8000.");
  }
}

  useEffect(() => {
    loginDemo();
  }, []);

  async function uploadFile(datasetType, file) {
  if (!file) return;

  const form = new FormData();
  form.append("dataset_type", datasetType);
  form.append("file", file);

  try {
    setMessage("Uploading file...");
    await fetch(`${API}/ingestion/upload/`, {
      method: "POST",
      body: form,
    });

    setMessage("File uploaded and validated.");
    await loadData();
    setActive("records");
  } catch {
    setMessage("Upload failed. Check file type and backend.");
  }
}

  async function approve(id) {
  try {
    await fetch(`${API}/review/records/${id}/approve/`, {
      method: "POST",
    });
    setMessage("Record approved and locked.");
    await loadData();
  } catch {
    setMessage("Could not approve this record.");
  }
}

  async function reject(id) {
  try {
    await fetch(`${API}/review/records/${id}/reject/`, {
      method: "POST",
    });
    setMessage("Record rejected.");
    await loadData();
  } catch {
    setMessage("Could not reject this record.");
  }
}
  return (
    <div className="app">
      <aside className="side">
        <div className="brandBlock">
          <div className="mark">B</div>
          <div>
            <div className="brand">BreatheESG</div>
            <div className="muted">Data Review Console</div>
          </div>
        </div>

        <button onClick={() => setActive("dashboard")} className={active === "dashboard" ? "nav active" : "nav"}>
          Overview
        </button>
        <button onClick={() => setActive("upload")} className={active === "upload" ? "nav active" : "nav"}>
          Upload Data
        </button>
        <button onClick={() => setActive("records")} className={active === "records" ? "nav active" : "nav"}>
          Review Records
        </button>
        <button onClick={() => setActive("failed")} className={active === "failed" ? "nav active" : "nav"}>
          Failed Rows
        </button>

        <div className="credit">
          <b>Built by kindey</b>
          <span>Audit-first prototype for ESG activity review.</span>
        </div>
      </aside>

      <main className="main">
        <div className="top">
          <div>
            <p className="label">Data quality workspace</p>
            <h1>{pageTitle(active)}</h1>
          </div>
          <button className="loginBtn" onClick={loginDemo}>
            {loggedIn ? "Demo connected" : "Demo login"}
          </button>
        </div>

        {message && <div className="notice">{message}</div>}

        {active === "dashboard" && <Dashboard summary={summary} records={records} />}
        {active === "upload" && <Upload uploadFile={uploadFile} />}
        {active === "records" && <Records records={records} approve={approve} reject={reject} />}
        {active === "failed" && <Failed failedRows={failedRows} />}
      </main>
    </div>
  );
}

function pageTitle(active) {
  if (active === "upload") return "Upload source data";
  if (active === "records") return "Review activity records";
  if (active === "failed") return "Inspect failed rows";
  return "Operational overview";
}

function Dashboard({ summary, records }) {
  const s = summary || {};

  return (
    <>
      <section className="heroClean">
        <div>
          <p className="label light">Source-to-audit workflow</p>
          <h2>Review incoming activity data before it becomes audit evidence.</h2>
          <p>
            The console keeps source rows traceable, standardizes usable records,
            flags uncertain inputs, and locks approved rows after analyst sign-off.
          </p>
        </div>
      </section>

      <section className="grid stats">
        <Stat title="Uploads" value={s.total_batches || 0} />
        <Stat title="Pending" value={s.pending_records || 0} />
        <Stat title="Flagged" value={s.flagged_records || 0} warn />
        <Stat title="Locked" value={s.approved_locked_records || 0} good />
        <Stat title="Failed" value={s.failed_rows || 0} bad />
      </section>

      <section className="card">
        <div className="sectionHead">
          <h3>Latest records</h3>
          <span>{records.length} records loaded</span>
        </div>
        <RecordTable records={records.slice(0, 7)} />
      </section>
    </>
  );
}

function Stat({ title, value, good, warn, bad }) {
  let cls = "statValue";
  if (good) cls += " good";
  if (warn) cls += " warn";
  if (bad) cls += " bad";

  return (
    <div className="stat card">
      <span>{title}</span>
      <div className={cls}>{value}</div>
    </div>
  );
}

function Upload({ uploadFile }) {
  const options = [
  [
    "SAP_ACTIVITY",
    "SAP Activity CSV",
    "Fuel and procurement activity standardized into audit-ready ESG records.",
  ],
  [
    "UTILITY_ELECTRICITY",
    "Utility Electricity CSV",
    "Electricity consumption normalized into standard energy usage records.",
  ],
  [
    "TRAVEL_ACTIVITY",
    "Travel Activity CSV",
    "Business travel activity reviewed for missing, suspicious and outlier values.",
  ],
];

  return (
    <section className="uploadGrid">
      {options.map(([key, title, text]) => (
        <div className="card uploadBox" key={key}>
          <span className="chip">{key}</span>
          <h3>{title}</h3>
          <p>{text}</p>
          <label className="fileBtn">
            Choose file
            <input hidden type="file" onChange={(e) => uploadFile(key, e.target.files[0])} />
          </label>
        </div>
      ))}
    </section>
  );
}

function Records({ records, approve, reject }) {
  return (
    <section className="card">
      <RecordTable records={records} approve={approve} reject={reject} actions />
    </section>
  );
}

function RecordTable({ records, approve, reject, actions = false }) {
  if (!records.length) return <div className="empty">No records yet.</div>;

  return (
    <div className="tableWrap">
      <table>
        <thead>
          <tr>
            <th>Source</th>
            <th>Activity</th>
            <th>Scope</th>
            <th>Raw Value</th>
            <th>Standardized</th>
            <th>Issues</th>
            <th>Expected Range</th>
            <th>Status</th>
            {actions && <th>Action</th>}
          </tr>
        </thead>
        <tbody>
          {records.map((r) => (
            <tr key={r.id}>
              <td>{cleanName(r.dataset_type)}</td>
              <td>{r.activity_type}</td>
              <td>{r.scope}</td>
              <td>
  {r.original_quantity ?? "-"} {r.original_unit || ""}
</td>

<td>
  {r.normalized_quantity ?? "-"} {r.normalized_unit || ""}
</td>

<td>
  {r.issues?.length
    ? r.issues.map((issue) => issue.message).join(", ")
    : "No issues"}
</td>
<td>{getExpectedRange(r)}</td>
              <td><span className={`badge ${r.review_status.toLowerCase()}`}>{r.review_status}</span></td>
              {actions && (
                <td>
                  <div className="actions">
                    <button disabled={r.is_locked} onClick={() => approve(r.id)}>Approve</button>
                    <button disabled={r.is_locked} onClick={() => reject(r.id)} className="reject">Reject</button>
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Failed({ failedRows }) {
  if (!failedRows.length) return <div className="card empty">No failed rows.</div>;

  return (
    <div className="failedStack">
      {failedRows.map((row) => (
        <div className="card failCard" key={row.id}>
          <h3>Row {row.row_number}</h3>
          <p>{row.failure_reason}</p>
          <pre>{JSON.stringify(row.raw_payload, null, 2)}</pre>
        </div>
      ))}
    </div>
  );
}

function cleanName(value) {
  return value.replaceAll("_", " ");
}
function getExpectedRange(record) {
  if (record.dataset_type === "SAP_ACTIVITY" && record.scope === "SCOPE_1") {
    return "Fuel: 0–100,000 L";
  }

  if (record.dataset_type === "SAP_ACTIVITY" && record.scope === "SCOPE_3") {
    return "Procurement: ₹1–₹1,00,00,000";
  }

  if (record.dataset_type === "UTILITY_ELECTRICITY") {
    return "Electricity: 0–100,000 kWh";
  }

  if (record.dataset_type === "TRAVEL_ACTIVITY") {
    return "Travel: 0–10,000 km";
  }

  return "Review manually";
}
export default App;