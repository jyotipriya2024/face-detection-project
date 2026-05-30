import { cn } from "@/lib/utils";

export function Card({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("rounded-xl border relative overflow-hidden", className)}
      style={{ background: "rgba(8,20,40,0.80)", borderColor: "rgba(0,200,255,0.14)" }}
      {...props}
    >
      {/* Top shimmer line */}
      <div className="absolute top-0 left-0 right-0 h-px"
           style={{ background: "linear-gradient(90deg,transparent,rgba(0,200,255,0.30),transparent)" }} />
      {children}
    </div>
  );
}

export function CardHeader({ className, children }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("px-5 pt-4 pb-2", className)}>{children}</div>;
}

export function CardContent({ className, children }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("px-5 pb-5", className)}>{children}</div>;
}

export function CardTitle({ className, children }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("text-sm font-semibold text-[#c8e8ff]", className)}>{children}</h3>;
}
