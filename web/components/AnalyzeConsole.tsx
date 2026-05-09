"use client";

import { AlertTriangle, LoaderCircle, RotateCcw, Search, ShieldCheck } from "lucide-react";
import { FormEvent, useState } from "react";
import { analyzeTweet } from "@/lib/api";
import type { AnalysisResult } from "@/lib/types";

export function AnalyzeConsole() {
    const [tweetUrl, setTweetUrl] = useState("");
    const [text, setText] = useState("");
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    async function onSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const nextResult = await analyzeTweet({
                tweet_url: tweetUrl.trim() || undefined,
                text: text.trim() || undefined
            });
            setResult(nextResult);
        } catch (caught) {
            setError(caught instanceof Error ? caught.message : "Analysis failed");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="dashboard-grid">
            <section className="panel" aria-labelledby="analyze-title">
                <div className="panel-header">
                    <div>
                        <h1 className="panel-title" id="analyze-title">
                            Tweet credibility check
                        </h1>
                        <p className="panel-subtitle">Paste tweet text, a tweet URL, or both.</p>
                    </div>
                    <ShieldCheck color="var(--teal)" aria-hidden="true" />
                </div>
                <form className="form" onSubmit={onSubmit}>
                    <label className="field-label">
                        Tweet URL
                        <input
                            className="input"
                            value={tweetUrl}
                            onChange={(event) => setTweetUrl(event.target.value)}
                            placeholder="https://x.com/user/status/123"
                        />
                    </label>
                    <label className="field-label">
                        Tweet text
                        <textarea
                            className="textarea"
                            value={text}
                            onChange={(event) => setText(event.target.value)}
                            placeholder="Paste the tweet content here when direct X lookup is not configured."
                        />
                    </label>
                    <div className="button-row">
                        <button className="button" type="submit" disabled={loading || (!tweetUrl.trim() && !text.trim())}>
                            {loading ? <LoaderCircle className="spin" size={18} /> : <Search size={18} />}
                            Analyze
                        </button>
                        <button
                            className="button secondary"
                            type="button"
                            onClick={() => {
                                setTweetUrl("");
                                setText("");
                                setResult(null);
                                setError(null);
                            }}
                        >
                            <RotateCcw size={18} />
                            Reset
                        </button>
                    </div>
                </form>
            </section>

            <aside className="panel" aria-label="System status">
                <div className="panel-header">
                    <div>
                        <h2 className="panel-title">MVP guardrails</h2>
                        <p className="panel-subtitle">Signals are stored for review and future rule tuning.</p>
                    </div>
                </div>
                <div className="status-strip">
                    <div className="metric">
                        <strong>3</strong>
                        <span>verdict states</span>
                    </div>
                    <div className="metric">
                        <strong>0.5</strong>
                        <span>neutral user credit</span>
                    </div>
                    <div className="metric">
                        <strong>v1</strong>
                        <span>ruleset</span>
                    </div>
                </div>
            </aside>

            {error ? (
                <section className="result-panel" aria-live="polite">
                    <div className="verdict-line">
                        <span className="verdict suspicious">
                            <AlertTriangle size={18} /> Error
                        </span>
                    </div>
                    <p className="reasoning">{error}</p>
                </section>
            ) : null}

            {result ? <AnalysisResultPanel result={result} /> : null}
        </div>
    );
}

function AnalysisResultPanel({ result }: Readonly<{ result: AnalysisResult }>) {
    return (
        <section className="result-panel" aria-live="polite">
            <div className="verdict-line">
                <span className={`verdict ${result.verdict}`}>
                    {result.verdict === "suspicious" ? <AlertTriangle size={18} /> : <ShieldCheck size={18} />}
                    {result.verdict.replace("_", " ")}
                </span>
                <strong>{Math.round(result.confidence * 100)}%</strong>
            </div>
            <p className="reasoning">{result.reasoning}</p>
            <ul className="list">
                {result.signals
                    .filter((signal) => signal.weight !== 0)
                    .slice(0, 5)
                    .map((signal) => (
                        <li key={signal.name}>
                            <strong>{signal.name.replaceAll("_", " ")}</strong>: {signal.description}
                        </li>
                    ))}
            </ul>
            <ul className="list">
                {result.claims.slice(0, 3).map((claim) => (
                    <li key={claim.text}>{claim.text}</li>
                ))}
            </ul>
            <p className="panel-subtitle">{result.disclaimer}</p>
        </section>
    );
}
