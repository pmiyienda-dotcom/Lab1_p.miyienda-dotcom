import csv
import sys
import os


# ─────────────────────────────────────────────
#  CSV LOADING
# ─────────────────────────────────────────────

def load_csv_data():
    """Prompt for a filename, validate it, and return a list of assignment dicts."""
    filename = input("Enter the name of the CSV file to process (e.g., grades.csv): ").strip()

    # Error handling: empty filename input
    if not filename:
        print("Error: No filename entered. Please provide a valid CSV filename.")
        sys.exit(1)

    # Error handling: wrong file extension
    if not filename.endswith(".csv"):
        print(f"Error: '{filename}' is not a CSV file. Please provide a file ending in .csv")
        sys.exit(1)

    # Error handling: file does not exist
    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        print("Make sure the file exists.")
        sys.exit(1)

    assignments = []
    try:
        with open(filename, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Error handling: missing required columns
            required_columns = {"assignment", "group", "score", "weight"}
            if not required_columns.issubset(set(reader.fieldnames or [])):
                missing = required_columns - set(reader.fieldnames or [])
                print(f"Error: The CSV file is missing required columns: {', '.join(missing)}")
                sys.exit(1)

            for line_number, row in enumerate(reader, start=2):
                assignment = row["assignment"].strip()
                group      = row["group"].strip()

                # Data validation: skip rows with empty assignment or group
                if not assignment or not group:
                    print(f"Warning: Row {line_number} has an empty assignment or group. Skipping.")
                    continue

                # Data validation: group must be Formative or Summative
                if group.lower() not in ("formative", "summative"):
                    print(f"Warning: Row {line_number} has an unrecognised group '{group}'. Skipping.")
                    continue


                # Error handling: blank score
                if not row["score"].strip():
                    print(f"Error: Row {line_number} ('{assignment}') is missing a score. Missing marks!")
                    sys.exit(1)

                # Error handling: score must be numerical
                try:
                    score = float(row["score"])
                except ValueError:
                    print(f"Error: Row {line_number} ('{assignment}') has an invalid score '{row["score"]}'. Score must be a number.")
                    print("Please fix your CSV file and run the program again.")
                    sys.exit(1)

                # Error handling: blank weight
                if not row["weight"].strip():
                    print(f"Error: Row {line_number} ('{assignment}') is missing a weight. Missing marks!")
                    sys.exit(1)

                # Error handling: weight must be numerical
                try:
                    weight = float(row["weight"])
                except ValueError:
                    print(f"Error: Row {line_number} ('{assignment}') has an invalid weight '{row["weight"]}'. Weight must be a number.")
                    print("Please fix your CSV file and run the program again.")
                    sys.exit(1)


                # Data validation: weight must be positive
                if weight <= 0:
                    print(f"Warning: Row {line_number} ('{assignment}') has a weight of {weight}. Weight must be positive. Skipping.")
                    continue

                assignments.append({
                    "assignment": assignment,
                    "group":      group,
                    "score":      score,
                    "weight":     weight,
                })

    except PermissionError:
        print(f"Error: Permission denied when trying to read '{filename}'.")
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: Could not read '{filename}'. Make sure the file is saved as UTF-8.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        sys.exit(1)

    # Error handling: no valid rows after parsing
    if not assignments:
        print("Error: No valid data found in the CSV file. Nothing to evaluate.")
        sys.exit(1)

    return assignments


# ─────────────────────────────────────────────
#  GRADE EVALUATION
# ─────────────────────────────────────────────

def evaluate_grades(data):
    """Run all validations, compute results, and print the final report."""
    print("GRADE EVALUATION REPORT")

    # a) Score validation (0-100)
    print("\nScore Validation")
    invalid = [(r["assignment"], r["score"]) for r in data
               if not (0 <= r["score"] <= 100)]
    if invalid:
        print("The following assignments have scores outside 0-100:")
        for name, sc in invalid:
            print(f"  {name}: {sc}")
    else:
        print("All scores are valid (0-100)")

    # b) Weight validation
    print("\nWeight Validation")
    total_w     = sum(r["weight"] for r in data)
    summative_w = sum(r["weight"] for r in data if r["group"].lower() == "summative")
    formative_w = sum(r["weight"] for r in data if r["group"].lower() == "formative")

    def check(label, actual, expected):
        print(f"{label}: {actual}%  (expected {expected}%)")

    check("Total weight    ", total_w,     100)
    check("Summative weight", summative_w,  40)
    check("Formative weight", formative_w,  60)

    # Error handling: stop if weights are invalid before calculating
    has_weight_error = False

    if total_w != 100:
        print(f"Error: Total weight is {total_w}%. All assignment weights must add up to exactly 100%.")
        has_weight_error = True

    if summative_w != 40:
        print(f"Error: Summative weight is {summative_w}%. Summative assignments must add up to exactly 40%.")
        has_weight_error = True

    if formative_w != 60:
        print(f"Error: Formative weight is {formative_w}%. Formative assignments must add up to exactly 60%.")
        has_weight_error = True

    if has_weight_error:
        print("\nPlease fix the weights in your CSV file and run the program again.")
        sys.exit(1)

    # c) Final grade & GPA
    final_grade = sum(r["score"] * (r["weight"] / 100) for r in data)
    gpa         = (final_grade / 100) * 5.0

    print("\nFinal Grade & GPA")
    print(f"Final Grade : {final_grade:.2f}%")
    print(f"GPA         : {gpa:.2f} / 5.0")

    # d) Category scores
    def category_score(group):
        """Return the percentage score for a given category group."""
        recs     = [r for r in data if r["group"].lower() == group]
        weighted = sum(r["score"] * (r["weight"] / 100) for r in recs)
        total_w  = sum(r["weight"] for r in recs)
        return (weighted / total_w) * 100 if total_w else 0

    summative_pct = category_score("summative")
    formative_pct = category_score("formative")

    print("\nCategory Scores")
    print(f"Summative : {summative_pct:.2f}%")
    print(f"Formative : {formative_pct:.2f}%")

    # e) Pass / Fail
    status = "PASSED" if summative_pct >= 50 and formative_pct >= 50 else "FAILED"

    # f) Resubmission logic
    failed_formative = [r for r in data
                        if r["group"].lower() == "formative" and r["score"] < 50]

    resubmission_candidates = []
    if failed_formative:
        highest_weight = max(r["weight"] for r in failed_formative)
        resubmission_candidates = [r for r in failed_formative
                                   if r["weight"] == highest_weight]

    # g) Final decision summary
    print("\nFINAL DECISION SUMMARY")
    print(f"Final Grade     : {final_grade:.2f}%")
    print(f"GPA             : {gpa:.2f} / 5.0")
    print(f"Summative Score : {summative_pct:.2f}%")
    print(f"Formative Score : {formative_pct:.2f}%")

    if status == "PASSED":
        print("FINAL DECISION: PASSED")
        print("The student met the 50% threshold in both categories.")
    else:
        print("FINAL DECISION: FAILED")
        if summative_pct < 50:
            print(f"Summative score ({summative_pct:.2f}%) is below 50%.")
        if formative_pct < 50:
            print(f"Formative score ({formative_pct:.2f}%) is below 50%.")

    if failed_formative:
        print("\nFAILED FORMATIVE ASSIGNMENTS:")
        for r in failed_formative:
            print(f"{r['assignment']}: Score = {r['score']}%, Weight = {r['weight']}%")
        print("\nRESUBMISSION ELIGIBLE:")
        if len(resubmission_candidates) == 1:
            print("Highest-weight failed formative assignment:")
        else:
            print(f"Tied at highest weight of {resubmission_candidates[0]['weight']}%:")
        for r in resubmission_candidates:
            print(f"{r['assignment']}: Score = {r['score']}%, Weight = {r['weight']}%")
    else:
        print("\nNo resubmission required.")
        print("All formative assignments scored 50% or above.")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    course_data = load_csv_data()
    evaluate_grades(course_data)