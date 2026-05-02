import type { Metadata } from "next";
import "./globals.css";
import SidebarNav from "@/components/SidebarNav";

export const metadata: Metadata = {
  title: "Vectorless RAG",
  description: "Production-ready RAG using PostgreSQL full-text search",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="flex h-full overflow-hidden bg-gray-100 font-sans antialiased">
        <SidebarNav />
        <main className="flex flex-1 flex-col overflow-hidden">{children}</main>
      </body>
    </html>
  );
}
