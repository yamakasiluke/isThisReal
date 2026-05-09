import { ShieldCheck } from "lucide-react";
import Link from "next/link";

export function AppChrome({ children }: Readonly<{ children: React.ReactNode }>) {
    return (
        <div className="app-shell">
            <header className="topbar">
                <Link className="brand" href="/">
                    <span className="brand-mark" aria-hidden="true">
                        <ShieldCheck size={19} />
                    </span>
                    <span>Is This Real</span>
                </Link>
                <nav className="nav" aria-label="Primary navigation">
                    <Link href="/analyze">Analyze</Link>
                    <Link href="/history">History</Link>
                    <Link href="/admin">Admin</Link>
                </nav>
            </header>
            <main className="main">{children}</main>
        </div>
    );
}
