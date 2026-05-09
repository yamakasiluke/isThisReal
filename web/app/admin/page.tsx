import { ClipboardList, Gauge, Users } from "lucide-react";
import { AppChrome } from "@/components/AppChrome";

export default function AdminPage() {
    return (
        <AppChrome>
            <section className="panel">
                <div className="panel-header">
                    <div>
                        <h1 className="panel-title">Reviewer operations</h1>
                        <p className="panel-subtitle">Rule changes, review queues, and credit audits land here as the system matures.</p>
                    </div>
                </div>
                <div className="status-strip">
                    <div className="metric">
                        <ClipboardList size={20} color="var(--teal)" />
                        <strong>rules_v1</strong>
                        <span>active ruleset</span>
                    </div>
                    <div className="metric">
                        <Users size={20} color="var(--coral)" />
                        <strong>0.5</strong>
                        <span>neutral credit baseline</span>
                    </div>
                    <div className="metric">
                        <Gauge size={20} color="var(--gold)" />
                        <strong>15%</strong>
                        <span>max credit confidence swing</span>
                    </div>
                </div>
            </section>
        </AppChrome>
    );
}
