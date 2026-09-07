"""Generate raw telecom source data: subscribers, call detail records (CDR),
and monthly billing — the inputs to a star-schema warehouse.
"""
import csv
import os
import random
from datetime import date

RAW = os.path.join("data", "raw")
PLANS = [("BASIC", 25.0), ("PLUS", 45.0), ("PREMIUM", 75.0), ("UNLIMITED", 95.0)]
REGIONS = ["North", "South", "East", "West"]
MONTHS = ["2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06"]


def main(n_subs: int = 4000):
    os.makedirs(RAW, exist_ok=True)
    subs = []
    for i in range(n_subs):
        plan, price = random.choice(PLANS)
        subs.append((f"SUB{i:06d}", plan, price, random.choice(REGIONS),
                     random.choice(MONTHS[:3])))  # signup month
    _write("subscribers.csv", ["subscriber_id", "plan", "monthly_price", "region", "signup_month"], subs)

    billing = []
    for sid, plan, price, region, signup in subs:
        active = True
        for m in MONTHS:
            if m < signup:
                continue
            # ~4% monthly churn
            if active and random.random() < 0.04 and m > signup:
                active = False
            if active:
                # usage-based add-ons
                addon = round(random.uniform(0, 30), 2)
                billing.append((sid, m, price, addon, round(price + addon, 2), 1))
            else:
                billing.append((sid, m, price, 0.0, 0.0, 0))   # churned = inactive
    _write("billing.csv", ["subscriber_id", "bill_month", "base_charge", "addons", "total_billed", "active"], billing)
    print(f"Wrote {len(subs):,} subscribers, {len(billing):,} monthly billing rows -> {RAW}")


def _write(name, header, rows):
    with open(os.path.join(RAW, name), "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)


if __name__ == "__main__":
    main()
