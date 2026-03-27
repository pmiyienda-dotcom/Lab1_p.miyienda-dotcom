import csv
import sys
import os
import sqlite3
from datetime import datetime


# ─────────────────────────────────────────────
#  DATABASE SETUP
# ─────────────────────────────────────────────

def init_db(db_path="grades.db"):
    """Create the SQLite database and tables if they do not yet exist."""
    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS assignments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id     INTEGER NOT NULL,
            assignment TEXT    NOT NULL,
            grp        TEXT    NOT NULL,
            score      REAL    NOT NULL,
            weight     REAL    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS results (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id              INTEGER NOT NULL UNIQUE,
            run_date            TEXT    NOT NULL,
            final_grade         REAL    NOT NULL,
            gpa                 REAL    NOT NULL,
            summative_pct       REAL    NOT NULL,
            formative_pct       REAL    NOT NULL,
            status              TEXT    NOT NULL,
            resubmission_target TEXT
        );
    """)
    conn.commit()
    return conn


def next_run_id(conn):
    """Return the next sequential run id."""
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(run_id), 0) + 1 FROM results")
    return cur.fetchone()[0]


def save_to_db(conn, run_id, data, final_grade, gpa,
               summative_pct, formative_pct, status, resubmission_names):
    """Persist one evaluation run to the database."""
    cur = conn.cursor()
    run_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for record in data:
        cur.execute(
            "INSERT INTO assignments (run_id, assignment, grp, score, weight) VALUES (?,?,?,?,?)",
            (run_id, record["assignment"], record["group"],
             record["score"], record["weight"])
        )

    cur.execute(
        """INSERT INTO results
           (run_id, run_date, final_grade, gpa, summative_pct,
            formative_pct, status, resubmission_target)
           VALUES (?,?,?,?,?,?,?,?)""",
        (run_id, run_date, final_grade, gpa, summative_pct,
         formative_pct, status, ", ".join(resubmission_names) or None)
    )
    conn.commit()
    print(f"\n  ✔ Results saved to grades.db  (run_id = {run_id})")


# ─────────────────────────────────────────────
#  CSV LOADING
# ─────────────────────────────────────────────

def load_csv_data():
    """Prompt for a filename, validate it, and return a list of assignment dicts."""
    filename = input("Enter the name of the CSV file to process (e.g., grades.csv): ").strip()

    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)

    assignments = []
    try:
        with open(filename, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                assignments.append({
                    "assignment": row["assignment"].strip(),
                    "group":      row["group"].strip(),
                    "score":      float(row["score"]),
                    "weight":     float(row["weight"]),
                })
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)

    if not assignments:
        print("Error: The CSV file is empty. Nothing to evaluate.")
        sys.exit(1)

    return assignments


# ─────────────────────────────────────────────
#  GRADE EVALUATION
# ─────────────────────────────────────────────

def evaluate_grades(data, conn):
    print("\n" + "=" * 50)
    print("         GRADE EVALUATION REPORT")
    print("=" * 50)

    # ── a) Score validation (0–100) ──────────────────
    print("\n--- Score Validation ---")
    invalid = [(r["assignment"], r["score"]) for r in data
               if not (0 <= r["score"] <= 100)]
    if invalid:
        print("The following assignments have scores outside 0–100:")
        for name, sc in invalid:
            print(f"  ✘ {name}: {sc}")
    else:
        print("  ✔ All scores are valid (0–100)")

    # ── b) Weight validation ─────────────────────────
    print("\n--- Weight Validation ---")
    total_w      = sum(r["weight"] for r in data)
    summative_w  = sum(r["weight"] for r in data if r["group"].lower() == "summative")
    formative_w  = sum(r["weight"] for r in data if r["group"].lower() == "formative")

    def check(label, actual, expected):
        mark = "✔" if actual == expected else "✘"
        print(f"  {mark} {label}: {actual}%  (expected {expected}%)")

    check("Total weight    ", total_w,     100)
    check("Summative weight", summative_w,  40)
    check("Formative weight", formative_w,  60)

    # ── c) Final grade & GPA ─────────────────────────
    final_grade = sum(r["score"] * (r["weight"] / 100) for r in data)
    gpa         = (final_grade / 100) * 5.0

    print("\n--- Final Grade & GPA ---")
    print(f"  Final Grade : {final_grade:.2f}%")
    print(f"  GPA         : {gpa:.2f} / 5.0")

    # ── d) Category scores & Pass/Fail ───────────────
    def category_score(group):
        recs = [r for r in data if r["group"].lower() == group]
        weighted = sum(r["score"] * (r["weight"] / 100) for r in recs)
        total_w  = sum(r["weight"] for r in recs)
        return (weighted / total_w) * 100 if total_w else 0

    summative_pct = category_score("summative")
    formative_pct = category_score("formative")

    print("\n--- Category Scores ---")
    print(f"  Summative : {summative_pct:.2f}%")
    print(f"  Formative : {formative_pct:.2f}%")

    status = "PASSED" if summative_pct >= 50 and formative_pct >= 50 else "FAILED"

    # ── e) Resubmission logic ────────────────────────
    failed_formative = [r for r in data
                        if r["group"].lower() == "formative" and r["score"] < 50]

    resubmission_candidates = []
    if failed_formative:
        highest_weight = max(r["weight"] for r in failed_formative)
        resubmission_candidates = [r for r in failed_formative
                                   if r["weight"] == highest_weight]

    resubmission_names = [r["assignment"] for r in resubmission_candidates]

    # ── f) Final decision summary ────────────────────
    print("\n" + "=" * 50)
    print("          FINAL DECISION SUMMARY")
    print("=" * 50)
    print(f"\n  Final Grade     : {final_grade:.2f}%")
    print(f"  GPA             : {gpa:.2f} / 5.0")
    print(f"  Summative Score : {summative_pct:.2f}%")
    print(f"  Formative Score : {formative_pct:.2f}%")
    print("-" * 50)

    if status == "PASSED":
        print("  ✔ FINAL DECISION: PASSED")
        print("    The student met the 50% threshold in both categories.")
    else:
        print("  ✘ FINAL DECISION: FAILED")
        if summative_pct < 50:
            print(f"    • Summative score ({summative_pct:.2f}%) is below 50%.")
        if formative_pct < 50:
            print(f"    • Formative score ({formative_pct:.2f}%) is below 50%.")

    print("-" * 50)

    if failed_formative:
        print("\n  FAILED FORMATIVE ASSIGNMENTS:")
        for r in failed_formative:
            print(f"    - {r['assignment']}: Score = {r['score']}%, Weight = {r['weight']}%")

        print("\n  RESUBMISSION ELIGIBLE:")
        if len(resubmission_candidates) == 1:
            print("    (highest-weight failed formative assignment)")
        else:
            print(f"    (tied at highest weight of {resubmission_candidates[0]['weight']}%)")
        for r in resubmission_candidates:
            print(f"    → {r['assignment']}: Score = {r['score']}%, Weight = {r['weight']}%")
    else:
        print("\n  No resubmission required.")
        print("  All formative assignments scored 50% or above.")

    print("=" * 50)

    # ── Persist to DB ────────────────────────────────
    run_id = next_run_id(conn)
    save_to_db(conn, run_id, data, final_grade, gpa,
               summative_pct, formative_pct, status, resubmission_names)

    return {
        "final_grade": final_grade, "gpa": gpa,
        "summative_pct": summative_pct, "formative_pct": formative_pct,
        "status": status, "resubmission": resubmission_names
    }


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    conn        = init_db("grades.db")
    course_data = load_csv_data()
    evaluate_grades(course_data, conn)
    conn.close()
