import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "CirclePortal - 東京工科大学サークル情報",
    description: "東京工科大学のサークル情報を探せるポータルサイト",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="ja">
            <body className={inter.className}>{children}</body>
        </html>
    );
}
