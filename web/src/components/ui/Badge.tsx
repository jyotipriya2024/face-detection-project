import { cn } from "@/lib/utils";

type BadgeVariant = "default" | "live" | "new" | "success" | "warning" | "danger" | "purple";

const variants: Record<BadgeVariant, string> = {
  default:  "bg-[rgba(0,200,255,0.10)] text-[#00c8ff] border-[rgba(0,200,255,0.28)]",
  live:     "bg-[rgba(255,77,109,0.10)] text-[#ff4d6d] border-[rgba(255,77,109,0.30)]",
  new:      "bg-[rgba(0,200,255,0.10)] text-[#00c8ff] border-[rgba(0,200,255,0.28)]",
  success:  "bg-[rgba(0,230,118,0.10)] text-[#00e676] border-[rgba(0,230,118,0.28)]",
  warning:  "bg-[rgba(255,171,64,0.10)] text-[#ffab40] border-[rgba(255,171,64,0.28)]",
  danger:   "bg-[rgba(255,77,109,0.10)] text-[#ff4d6d] border-[rgba(255,77,109,0.28)]",
  purple:   "bg-[rgba(123,97,255,0.10)] text-[#7b61ff] border-[rgba(123,97,255,0.28)]",
};

export function Badge({
  variant = "default", className, children,
}: { variant?: BadgeVariant; className?: string; children: React.ReactNode }) {
  return (
    <span className={cn(
      "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[0.62rem] font-bold tracking-wide border uppercase",
      variants[variant], className
    )}>
      {children}
    </span>
  );
}
