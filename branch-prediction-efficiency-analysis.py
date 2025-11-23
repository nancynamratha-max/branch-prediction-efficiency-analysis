# Branch Prediction Efficiency Analyzer (simple, interactive)
# Implements: Always Taken, Always Not Taken, 1-bit, 2-bit predictors
import random
import pandas as pd
import matplotlib.pyplot as plt

# Predictor implementations
def always_taken(pattern): return ["T"] * len(pattern)
def always_not(pattern):  return ["N"] * len(pattern)

def one_bit(pattern, init='T'):
    bit = init
    preds = []
    for actual in pattern:
        preds.append(bit)
        bit = actual   # update to last outcome
    return preds

def two_bit(pattern, init=3):
    state = init
    preds = []
    for actual in pattern:
        pred = 'T' if state >= 2 else 'N'
        preds.append(pred)
        if actual == 'T':
            if state < 3: state += 1
        else:
            if state > 0: state -= 1
    return preds

# Utilities
def read_pattern_from_user():
    print("\nEnter a branch pattern (use T for taken, N for not taken).")
    print("Examples: T N T T N  OR  TTTTNN (no spaces).")
    s = input("Pattern (or press Enter to use sample patterns): ").strip()
    if s == "":
        return None
    # allow spaces or no-spaces
    if " " in s:
        parts = [p.upper() for p in s.split() if p.strip()!='']
    else:
        parts = [c.upper() for c in s.strip() if c.upper() in ('T','N')]
    return parts

def stats(preds, actual):
    total = len(actual)
    correct = sum(1 for p,a in zip(preds, actual) if p==a)
    wrong = total - correct
    acc = round(correct/total*100,2) if total>0 else 0.0
    mis = round(100-acc,2)
    return total, correct, wrong, acc, mis

def print_predictions(label, preds):
    print(f"{label:14}: {' '.join(preds)}")

def print_correct_marks(preds, actual):
    marks = ["✓" if p==a else "X" for p,a in zip(preds, actual)]
    print(f"{'Correct':14}: {' '.join(marks)}")

# Main interactive flow 
def main():
    print("Branch Prediction Efficiency Analyzer (interactive)\n")
    print("You can enter one or more patterns. If you press Enter without input,")
    print("the program will use some sample patterns (loop, alternating, random, biased).")

    user_pat = read_pattern_from_user()
    patterns = {}
    if user_pat:
        patterns["user_pattern"] = user_pat
    else:
        patterns = {
            "loop_pattern": list("T T T T T T T T T T".split()),
            "alternating": list("T N T N T N T N T N".split()),
            "random": [random.choice(['T','N']) for _ in range(10)],
            "biased_not": list("N N N N T N N N N N".split())
        }

    all_results = []
    for name, pattern in patterns.items():
        print("\n" + "="*60)
        print(f"Branch pattern used ({name}):")
        print("Pattern     :", ' '.join(pattern))
        print("-"*60)

        methods = {
            "Always Taken": always_taken(pattern),
            "Always Not": always_not(pattern),
            "1-bit": one_bit(pattern, init='T'),
            "2-bit": two_bit(pattern, init=3)
        }

        summary = []
        print_predictions("Actual", pattern)
        for mname, preds in methods.items():
            print_predictions(mname, preds)
            print_correct_marks(preds, pattern)
            total, correct, wrong, acc, mis = stats(preds, pattern)
            print(f"{'Accuracy':14}: {acc}%   (Correct: {correct}, Wrong: {wrong})\n")
            summary.append({
                "Pattern": name,
                "Predictor": mname,
                "Total": total,
                "Correct": correct,
                "Wrong": wrong,
                "Accuracy(%)": acc,
                "Misprediction(%)": mis
            })

        df = pd.DataFrame(summary)
        all_results.append(df)

        # display summary table
        print("-"*60)
        print("Summary table for this pattern:")
        display_df = df[["Predictor","Total","Correct","Wrong","Accuracy(%)","Misprediction(%)"]].set_index("Predictor")
        print(display_df.to_string())
        print("="*60)

        # plot accuracies for this pattern
        plt.figure(figsize=(6,3))
        plt.bar(display_df.index, display_df["Accuracy(%)"])
        plt.title(f"Accuracy for pattern: {name}")
        plt.ylabel("Accuracy (%)")
        plt.ylim(0,100)
        plt.tight_layout()
        plt.show()

    # Combined results and overall bar chart
    combined = pd.concat(all_results, ignore_index=True)
    totals = combined.groupby("Predictor")["Total"].sum()
    corrects = combined.groupby("Predictor")["Correct"].sum()
    weighted_accuracy = (corrects / totals * 100).round(2)
    overall = pd.DataFrame({
        "Total": totals,
        "Correct": corrects,
        "Weighted Accuracy(%)": weighted_accuracy
    }).sort_values("Weighted Accuracy(%)", ascending=False)
    print("\n" + "#"*80)
    print("Overall comparison (all patterns combined):")
    print(overall.to_string())
    print("#"*80)

    plt.figure(figsize=(6,3))
    plt.bar(overall.index, overall["Weighted Accuracy(%)"])
    plt.title("Overall Weighted Accuracy by Predictor (all patterns)")
    plt.ylabel("Weighted Accuracy (%)")
    plt.ylim(0,100)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()