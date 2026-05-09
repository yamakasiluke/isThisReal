"use client";

import { RefreshCcw } from "lucide-react";
import { useEffect, useState } from "react";
import { listAnalyses } from "@/lib/api";
import type { AnalysisSummary } from "@/lib/types";

export function HistoryTable() {
    const [rows, setRows] = useState<AnalysisSummary[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    async function loadRows() {
        setLoading(true);
        setError(null);
        try {
            setRows(await listAnalyses());
        } catch (caught) {
            setError(caught instanceof Error ? caught.message : "Could not load history");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        void loadRows();
    }, []);

    return (
        <section className="table-panel">
            <div className="table-header">
                <div className="verdict-line">
                    <div>
                        <h1 className="panel-title">Analysis history</h1>
                        <p className="panel-subtitle">Recent website and bot checks share the same audit trail.</p>
                    </div>
                    <button className="button secondary" type="button" onClick={loadRows} disabled={loading}>
                        <RefreshCcw className={loading ? "spin" : undefined} size={18} />
                        Refresh
                    </button>
                </div>
            </div>
            {error ? <p className="empty-state">{error}</p> : null}
            {!error && rows.length === 0 ? <p className="empty-state">No analyses stored yet.</p> : null}
            {rows.length > 0 ? (
                <div style={{ overflowX: "auto" }}>
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Created</th>
                                <th>Source</th>
                                <th>Verdict</th>
                                <th>Confidence</th>
                                <th>Reasoning</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map((row) => (
                                <tr key={row.analysis_id}>
                                    <td>{new Date(row.created_at).toLocaleString()}</td>
                                    <td>{row.source}</td>
                                    <td>{row.verdict.replace("_", " ")}</td>
                                    <td>{Math.round(row.confidence * 100)}%</td>
                                    <td>{row.reasoning}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ) : null}
        </section>
    );
}
