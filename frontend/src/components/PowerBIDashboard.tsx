interface PowerBIDashboardProps {
  title?: string;
  reportId: string;
  ctid: string;
}

export default function PowerBIDashboard({
  title = "Dashboard",
  reportId,
  ctid,
}: PowerBIDashboardProps) {
  return (
    <div className="glass-card p-5">
      <h2 className="text-lg font-heading font-bold mb-4">{title}</h2>
      <div className="w-full overflow-hidden rounded-lg border border-border/50">
        <iframe
          title={title}
          src={`https://app.powerbi.com/reportEmbed?reportId=${reportId}&autoAuth=true&ctid=${ctid}&actionBarEnabled=true`}
          frameBorder="0"
          allowFullScreen
          className="w-full"
          style={{ height: "600px" }}
        />
      </div>
    </div>
  );
}
