export const metadata = {
  title: "MetricMind",
  description: "Governed conversational BI",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif", background: "#fafafa" }}>
        {children}
      </body>
    </html>
  );
}