const sizeMap = {
  sm: "h-4 w-4 border-2",
  md: "h-6 w-6 border-2",
  lg: "h-10 w-10 border-[3px]",
};

export default function Loader({ size = "md", label, className = "" }) {
  return (
    <div className={`flex items-center justify-center gap-3 ${className}`}>
      <div
        className={`animate-spin rounded-full border-white/10 border-t-violet-400 ${sizeMap[size]}`}
      />
      {label && <span className="text-sm text-slate-400">{label}</span>}
    </div>
  );
}
