export default function Loading() {
  return (
    <div className="space-y-5">
      <div className="h-16 animate-pulse rounded-2xl bg-white" />
      <div className="grid gap-4 md:grid-cols-4">
        {[0, 1, 2, 3].map((item) => (
          <div key={item} className="h-32 animate-pulse rounded-2xl bg-white" />
        ))}
      </div>
      <div className="h-96 animate-pulse rounded-2xl bg-white" />
    </div>
  );
}
