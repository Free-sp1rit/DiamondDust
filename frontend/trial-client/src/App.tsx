import { ChangeEvent, useEffect, useMemo, useState } from "react";

type JsonRecord = Record<string, unknown>;

type ModelPreset = {
  label: string;
  model: string;
  description?: string;
};

type ArtifactVersion = {
  run_id: string;
  created_at?: string;
  model?: string;
  validation_status?: string;
  unit_candidate_count?: number;
  relation_candidate_count?: number;
  deletable?: boolean;
};

type TrialNote = {
  path: string;
  name: string;
  size_bytes: number;
  artifact_versions?: ArtifactVersion[];
};

type TrialStatus = {
  provider: string;
  default_model: string;
  model_presets: ModelPreset[];
  api_key_present: boolean;
  api_key_env_var: string;
  secrets_env_file: string;
  workspace?: JsonRecord;
  input_dir?: string;
  vault_root?: string;
  notes: TrialNote[];
  boundaries?: JsonRecord;
};

type TrialResult = {
  run_id: string;
  quality_status?: string;
  quality_reasons?: string[];
  returncode?: number;
  succeeded?: boolean;
  stderr?: string;
  boundaries?: JsonRecord;
  artifact_paths?: JsonRecord;
  extraction_artifact?: JsonRecord;
};

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  const data = (await response.json()) as T & { error?: string };
  if (!response.ok) {
    throw new Error(data.error || "request failed");
  }
  return data;
}

function asRecord(value: unknown): JsonRecord {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as JsonRecord)
    : {};
}

function asArray<T>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : [];
}

function text(value: unknown): string {
  if (value === undefined || value === null || value === "") return "-";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return JSON.stringify(value);
}

export default function App() {
  const [status, setStatus] = useState<TrialStatus | null>(null);
  const [selectedNote, setSelectedNote] = useState("");
  const [model, setModel] = useState("");
  const [workspaceDir, setWorkspaceDir] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("loading");
  const [currentResult, setCurrentResult] = useState<TrialResult | null>(null);

  const artifact = asRecord(currentResult?.extraction_artifact);
  const units = asArray<JsonRecord>(artifact.unit_candidates);
  const relations = asArray<JsonRecord>(artifact.relation_candidates);
  const versions = useMemo(() => {
    return status?.notes.find((note) => note.path === selectedNote)?.artifact_versions || [];
  }, [selectedNote, status]);

  async function refresh() {
    const next = await api<TrialStatus>("/api/status");
    setStatus(next);
    setModel((previous) => previous || next.default_model);
    if (!selectedNote && next.notes.length) {
      setSelectedNote(next.notes[0].path);
    }
    setMessage("ready");
  }

  useEffect(() => {
    refresh().catch((error) => setMessage(error.message));
  }, []);

  async function saveApiKey() {
    if (!apiKey.trim()) {
      setMessage("请输入 API key");
      return;
    }
    setBusy(true);
    try {
      await api("/api/secrets/deepseek", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: apiKey })
      });
      setApiKey("");
      await refresh();
      setMessage("key saved locally");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "save failed");
    } finally {
      setBusy(false);
    }
  }

  async function configureWorkspace() {
    if (!workspaceDir.trim()) {
      setMessage("请输入工作目录");
      return;
    }
    setBusy(true);
    try {
      await api("/api/workspace", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ workspace_dir: workspaceDir })
      });
      await refresh();
      setMessage("workspace ready");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "workspace failed");
    } finally {
      setBusy(false);
    }
  }

  async function importFiles(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files || []);
    if (!files.length) return;
    setBusy(true);
    try {
      for (const file of files) {
        await api("/api/notes/import", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            filename: file.name,
            content: await file.text()
          })
        });
      }
      await refresh();
      setMessage(`imported ${files.length} note(s)`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "import failed");
    } finally {
      event.target.value = "";
      setBusy(false);
    }
  }

  async function runExtraction() {
    if (!selectedNote) {
      setMessage("请选择笔记");
      return;
    }
    setBusy(true);
    setMessage("running");
    try {
      const result = await api<TrialResult>("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          note_path: selectedNote,
          model
        })
      });
      setCurrentResult(result);
      await refresh();
      setMessage(result.run_id);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "run failed");
    } finally {
      setBusy(false);
    }
  }

  async function loadArtifact(runId: string) {
    setBusy(true);
    try {
      const result = await api<TrialResult>(
        `/api/artifact?run_id=${encodeURIComponent(runId)}`
      );
      setCurrentResult(result);
      setMessage(`loaded ${runId}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "load failed");
    } finally {
      setBusy(false);
    }
  }

  async function deleteArtifact(runId: string) {
    setBusy(true);
    try {
      await api("/api/artifact/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run_id: runId })
      });
      if (currentResult?.run_id === runId) setCurrentResult(null);
      await refresh();
      setMessage(`deleted ${runId}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "delete failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <h1>DiamondDust Trial</h1>
          <p>{message}</p>
        </div>
        <span className={status?.api_key_present ? "pill ok" : "pill warn"}>
          {status?.api_key_present ? "key ready" : "key missing"}
        </span>
      </header>

      <section className="layout">
        <aside className="sidebar">
          <section className="panel">
            <h2>本地配置</h2>
            <label>
              工作目录
              <input
                value={workspaceDir}
                onChange={(event) => setWorkspaceDir(event.target.value)}
                placeholder="例如 C:\\DiamondDustTrial"
              />
            </label>
            <button disabled={busy} onClick={configureWorkspace}>
              使用目录
            </button>
            <dl className="compact">
              <dt>输入目录</dt>
              <dd>{text(status?.workspace?.input_dir || status?.input_dir)}</dd>
              <dt>产物目录</dt>
              <dd>{text(status?.workspace?.vault_root || status?.vault_root)}</dd>
            </dl>
          </section>

          <section className="panel">
            <h2>Provider</h2>
            <label>
              DeepSeek API Key
              <input
                type="password"
                value={apiKey}
                onChange={(event) => setApiKey(event.target.value)}
                autoComplete="off"
              />
            </label>
            <button disabled={busy} onClick={saveApiKey}>
              保存到本机
            </button>
            <label>
              模型
              <select value={model} onChange={(event) => setModel(event.target.value)}>
                {(status?.model_presets || []).map((preset) => (
                  <option key={preset.model} value={preset.model}>
                    {preset.label}
                  </option>
                ))}
              </select>
            </label>
          </section>

          <section className="panel">
            <h2>笔记</h2>
            <input
              type="file"
              multiple
              accept=".md,.markdown,text/markdown"
              onChange={importFiles}
            />
            <select
              value={selectedNote}
              onChange={(event) => setSelectedNote(event.target.value)}
            >
              {(status?.notes || []).map((note) => (
                <option key={note.path} value={note.path}>
                  {note.name}
                </option>
              ))}
            </select>
            <div className="button-row">
              <button disabled={busy || !selectedNote} onClick={runExtraction}>
                运行提取
              </button>
              <button className="secondary" disabled={busy} onClick={refresh}>
                刷新
              </button>
            </div>
          </section>

          <section className="panel">
            <h2>历史版本</h2>
            <div className="stack">
              {versions.length ? (
                versions.map((version) => (
                  <article
                    className={
                      currentResult?.run_id === version.run_id
                        ? "version active"
                        : "version"
                    }
                    key={version.run_id}
                  >
                    <strong>{version.created_at || version.run_id}</strong>
                    <span>
                      {version.model || "-"} · {version.unit_candidate_count || 0} units ·{" "}
                      {version.relation_candidate_count || 0} relations
                    </span>
                    <div className="button-row">
                      <button
                        className="secondary"
                        disabled={busy}
                        onClick={() => loadArtifact(version.run_id)}
                      >
                        查看
                      </button>
                      <button
                        className="danger"
                        disabled={busy || !version.deletable}
                        onClick={() => deleteArtifact(version.run_id)}
                      >
                        删除
                      </button>
                    </div>
                  </article>
                ))
              ) : (
                <p className="muted">暂无历史产物</p>
              )}
            </div>
          </section>
        </aside>

        <section className="content">
          <section className="metrics">
            <Metric label="质量" value={currentResult?.quality_status || "-"} />
            <Metric label="Units" value={units.length} />
            <Metric label="Relations" value={relations.length} />
            <Metric label="Provider" value={text(artifact.provider || status?.provider)} />
          </section>

          <section className="result-grid">
            <section>
              <h2>Units</h2>
              <div className="stack">
                {units.length ? (
                  units.map((unit, index) => <UnitCard unit={unit} index={index} key={index} />)
                ) : (
                  <p className="muted">未加载产物</p>
                )}
              </div>
            </section>

            <section>
              <h2>Relations</h2>
              <div className="stack">
                {relations.length ? (
                  relations.map((relation, index) => (
                    <RelationCard relation={relation} key={index} />
                  ))
                ) : (
                  <p className="muted">无 relation</p>
                )}
              </div>
            </section>
          </section>
        </section>
      </section>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <article className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function UnitCard({ unit, index }: { unit: JsonRecord; index: number }) {
  return (
    <article className="unit-card">
      <header>
        <span className="pill">Unit {index + 1}</span>
        <h3>{text(unit.title || unit.id)}</h3>
      </header>
      <div className="chips">
        {[unit.type, unit.status, unit.confidence].map((value, chipIndex) => (
          <span className="chip" key={chipIndex}>
            {text(value)}
          </span>
        ))}
      </div>
      <p>{text(unit.content)}</p>
      <details>
        <summary>验证依据 source_refs</summary>
        <JsonBlock value={unit.source_refs} />
      </details>
      <details>
        <summary>机器结构</summary>
        <JsonBlock value={unit} />
      </details>
    </article>
  );
}

function RelationCard({ relation }: { relation: JsonRecord }) {
  return (
    <article className="relation-card">
      <h3>{text(relation.relation_type)}</h3>
      <dl className="compact">
        <dt>source</dt>
        <dd>{text(relation.source_id)}</dd>
        <dt>target</dt>
        <dd>{text(relation.target_id)}</dd>
        <dt>reason</dt>
        <dd>{text(relation.reason)}</dd>
      </dl>
      <details>
        <summary>机器结构</summary>
        <JsonBlock value={relation} />
      </details>
    </article>
  );
}

function JsonBlock({ value }: { value: unknown }) {
  return <pre>{JSON.stringify(value, null, 2)}</pre>;
}
