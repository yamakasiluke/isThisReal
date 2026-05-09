export type Verdict = "likely_true" | "suspicious" | "unclear";

export interface Signal {
    name: string;
    value: boolean | number | string | null;
    weight: number;
    priority: string;
    description: string;
}

export interface ExtractedClaim {
    text: string;
    claim_type: string;
    confidence: number;
}

export interface AnalysisResult {
    analysis_id: string;
    tweet_id: string | null;
    verdict: Verdict;
    confidence: number;
    reasoning: string;
    claims: ExtractedClaim[];
    signals: Signal[];
    suspicion_score: number;
    disclaimer: string;
    created_at: string;
}

export interface AnalysisSummary {
    analysis_id: string;
    tweet_key: string;
    source: string;
    verdict: Verdict;
    confidence: number;
    suspicion_score: number;
    reasoning: string;
    created_at: string;
}
