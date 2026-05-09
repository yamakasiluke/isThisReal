import type { AnalysisResult, AnalysisSummary } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function analyzeTweet(input: { text?: string; tweet_url?: string }): Promise<AnalysisResult> {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...input, source: "website" })
    });
    if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || "Analysis request failed");
    }
    return response.json();
}

export async function listAnalyses(): Promise<AnalysisSummary[]> {
    const response = await fetch(`${API_BASE_URL}/analyses?limit=50`, { cache: "no-store" });
    if (!response.ok) {
        throw new Error("Could not load analysis history");
    }
    return response.json();
}
