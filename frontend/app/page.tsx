export default function Home() {
  return (
    <main className="flex min-h-full flex-1 flex-col items-center justify-center gap-4 px-6 py-24">
      <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
        AI Knowledge Assistant
      </h1>
      <p className="max-w-md text-center text-zinc-600 dark:text-zinc-400">
        Next.js frontend scaffold — extend in <code className="font-mono text-sm">app/</code>,{" "}
        <code className="font-mono text-sm">components/</code>, and{" "}
        <code className="font-mono text-sm">lib/</code>.
      </p>
    </main>
  );
}
