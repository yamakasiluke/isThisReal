import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "Is This Real",
    description: "Tweet credibility checks for a website and X/Twitter bot"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
    return (
        <html lang="en">
            <body>{children}</body>
        </html>
    );
}
