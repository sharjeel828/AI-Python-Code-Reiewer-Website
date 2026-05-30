from app import app, db, Report

with app.app_context():
    r = Report.query.get(22)
    print("Report 22:", r)
    if r:
        print("Metrics:", repr(r.Metrics))
        print("Type:", type(r.Metrics))
        
    for r in Report.query.order_by(Report.ReportID.desc()).limit(5):
        print(f"Report {r.ReportID}: Metrics={repr(r.Metrics)}")
