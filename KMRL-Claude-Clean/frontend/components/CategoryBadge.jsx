export default function CategoryBadge({ category }) {
  return (
    <div className="inline-flex w-fit items-center gap-2 rounded-full border border-violet-400/20 bg-violet-400/10 px-3 py-1.5 text-sm font-medium text-violet-300">

      <span className="h-2 w-2 rounded-full bg-violet-400" />

      {category}

    </div>
  );
}