# AcadRisk AI: Machine Learning Methodology & Predictive Pipeline

## 1. Pedagogical Problem Framing & Objectives

Predicting student academic risk before the end of an academic semester is an asymmetric machine learning problem:
- **Cost of False Negatives (Type II Error):** Extremely high. If an at-risk student is misclassified as "Low Risk", faculty advisers are not notified, timely remedial tutorials are not scheduled, and the student fails or drops out.
- **Cost of False Positives (Type I Error):** Low. If a borderline passing student is flagged as "Medium Risk" or "High Risk", the consequence is an advisory check-in or mentoring invitation, which has zero harmful impact and often provides positive reinforcement.

Therefore, the AcadRisk AI machine learning architecture **prioritizes High-Risk Class Recall ($\ge 80\%$)** alongside overall accuracy and macro F1-score.

---

## 2. Dataset Analysis & Cross-Institutional Comparative Study

AcadRisk AI synthesizes empirical findings from two premier academic benchmarks in educational data mining:

```
+------------------------------------------------------------------------------------+
|                         Dataset Comparison Matrix                                  |
+--------------------------+------------------------------+--------------------------+
| Dimension                | UCI Student Performance      | IITR-APE Dataset         |
|                          | (Cortez & Silva, 2008)       | (Bachchas et al., 2021)  |
+--------------------------+------------------------------+--------------------------+
| Originating Institution  | Alentejo Region, Portugal    | IIT Roorkee, India       |
| Domain                   | Secondary Education (Math/Por)| Tertiary Engineering     |
| Sample Size              | 1,044 students (combined)    | 2,000+ course instances  |
| Grading Scale            | 0 - 20 point integer scale   | 100-point percentage scale|
| Continuous Assessment    | G1 (Period 1), G2 (Period 2) | CWS (25%), MTE (25%)     |
| Summative Target         | G3 (Final Exam)              | ETE (End Term Exam, 50%) |
| Behavioral Features      | Studytime, Absences, Alcohol | Attendance, Lab Marks,   |
|                          | Family Support, Internet     | Prerequisite SGPAs       |
+--------------------------+------------------------------+--------------------------+
```

### 2.1 UCI Student Performance Dataset (Cortez & Silva, 2008)
- Comprises demographic, social, and academic features collected from two Portuguese secondary schools.
- Provides 30 input attributes capturing:
  - Student personal and family background (`Medu`, `Fedu`, `Mjob`, `Fjob`, `famsize`, `Pstatus`).
  - Academic habits and institutional support (`studytime`, `failures`, `schoolsup`, `famsup`, `paid`, `activities`).
  - Social behaviors and health (`freetime`, `goout`, `Dalc`, `Walc`, `health`, `absences`).
  - Formative milestone evaluations: $G1$ (first period mark) and $G2$ (second period mark).

### 2.2 IITR-APE Dataset (Bachchas et al., 2021)
- Developed at the Indian Institute of Technology Roorkee (IIT Roorkee) specifically for engineering academic performance forecasting.
- Structures continuous assessment into three institutional pillars:
  1. **CWS (Class Work Sessional, 25 points):** Quizzes, assignments, and class participation.
  2. **MTE (Mid Term Examination, 25 points):** Comprehensive assessment administered at the 8th week.
  3. **ETE (End Term Examination, 50 points):** Summative evaluation.
- Demonstrates that early attendance and midterm marks ($CWS + MTE$) account for over **72% of the predictive variance** in final student outcomes.

### 2.3 Synthesis in AcadRisk AI
AcadRisk AI harmonizes both approaches:
- Continuous grading is scaled to a standard **100-point percentage scale**.
- Internal continuous assessment marks ($G1$ and $G2$ or internal midterm scores) and cumulative attendance percentages are mapped directly from the MySQL database schema (`assessments`, `marks`, `attendance_records`).
- Historical academic standing (cumulative SGPA/grade points from `academic_history`) provides longitudinal context.

---

## 3. Elimination of Target Leakage

> [!CAUTION]
> **Zero Target Leakage Guarantee:**
> In historical educational data mining literature, naive models frequently achieve artificial $> 95\%$ accuracy by including final exam scores ($G3$ or summative marks) in the feature matrix. AcadRisk AI strictly enforces an isolated feature engineering boundary:

1. **Feature Pruning:** The final target variable $G3$ is removed from the input matrix $\mathbf{X}$ prior to any transformation, imputation, or pipeline fitting:
   $$\mathbf{X} = \text{Dataset} \setminus \{G3\}$$
2. **Target Formulation:**
   - **Continuous Regression Target:**
     $$\text{Target Percentage} = \frac{G3}{20.0} \times 100$$
   - **Multi-Class Risk Target:**
     $$\text{Risk Category} = \begin{cases} 
     \text{"High Risk"} & \text{if } G3 < 10 \quad (\text{Score} < 50\%) \\
     \text{"Medium Risk"} & \text{if } 10 \le G3 < 14 \quad (50\% \le \text{Score} < 70\%) \\
     \text{"Low Risk"} & \text{if } G3 \ge 14 \quad (\text{Score} \ge 70\%)
     \end{cases}$$
3. **Pipeline Encapsulation:** All transformers (scalers, encoders, and imputers) are fit solely on the training split $\mathbf{X}_{\text{train}}$ and transformed downstream on $\mathbf{X}_{\text{test}}$, completely eliminating data snooping bias.

---

## 4. Feature Preprocessing Pipeline

The preprocessing pipeline is constructed using Scikit-Learn's `ColumnTransformer`:

```
Raw DB / CSV Features
   │
   ├── Numerical Features (G1, G2, studytime, failures, absences, past_sgpa, attendance_pct)
   │     │
   │     ├── SimpleImputer(strategy='median')
   │     └── StandardScaler()  ──> Z-score normalized [μ = 0, σ = 1]
   │
   └── Categorical Features (school, sex, address, famsize, Pstatus, Medu, Fedu, Mjob, ...)
         │
         ├── SimpleImputer(strategy='most_frequent')
         └── OneHotEncoder(handle_unknown='ignore', sparse_output=False)
```

- **Median Imputation** handles absent values without distortion from extreme outliers.
- **Z-Score Normalization** prevents attributes with large numerical scales (e.g., absences: 0–93) from dominating gradient descent over compact scales (e.g., study time: 1–4).
- **One-Hot Encoding with Unknown Handling** ensures robust inference even if an unseen category appears during runtime inference.

---

## 5. Model Architecture & Comparative Evaluation

Three distinct algorithmic paradigms were implemented, trained on identical cross-validation splits ($80\%$ train, $20\%$ test), and evaluated:

### 5.1 Evaluated Algorithms
1. **Multinomial Logistic Regression (`class_weight='balanced'`):**
   - Convex optimization using L2 regularization.
   - Balanced class weighting scales the loss function inversely proportional to class frequencies, directly boosting sensitivity to the minority High-Risk class.
2. **Random Forest Classifier (`n_estimators=100`, `max_depth=8`):**
   - Ensemble bagging model aggregating decorrelated decision trees.
   - Evaluates non-linear feature interactions (e.g., high study time failing to compensate for low attendance).
3. **Gradient Boosting Classifier (`n_estimators=100`, `learning_rate=0.1`):**
   - Sequential boosting minimizing logistic deviance loss.
   - High expressive power for complex decision boundaries.
4. **Random Forest Regressor (`n_estimators=100`, `max_depth=10`):**
   - Provides granular continuous final score estimation ($\hat{y} \in [0, 100\%]$).

### 5.2 Benchmark Performance Comparison

| Model | Test Accuracy | Macro Precision | Macro Recall | Macro F1-Score | High-Risk Class Recall | High-Risk Class F1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Balanced)** | **83.73%** | **83.81%** | **83.69%** | **83.75%** | **82.61%** | **82.61%** |
| Random Forest Classifier | 84.69% | 84.72% | 81.45% | 82.89% | 78.26% | 80.00% |
| Gradient Boosting Classifier | 82.30% | 82.01% | 80.12% | 80.95% | 73.91% | 77.27% |

### 5.3 Model Selection Decision
While Random Forest achieved slightly higher raw accuracy ($84.69\%$ vs $83.73\%$), **Logistic Regression with Balanced Class Weights was selected as the primary production classifier** because it achieved the **highest High-Risk Recall ($82.61\%$)**. In an institutional early warning system, capturing $> 82\%$ of truly failing students is vastly more critical than a nominal $0.96\%$ gain in overall accuracy.

---

## 6. Risk Threshold Determination

AcadRisk AI applies a two-tiered decision rule combining continuous score regression and class posterior probabilities:

$$\text{Final Risk Status} = \begin{cases}
\text{"HIGH RISK"} & \text{if } P(\text{High Risk}) \ge 0.50 \text{ OR } \hat{y}_{\text{score}} < 50.0\% \\
\text{"MEDIUM RISK"} & \text{if } 50.0\% \le \hat{y}_{\text{score}} < 70.0\% \text{ AND } P(\text{High Risk}) < 0.50 \\
\text{"LOW RISK"} & \text{if } \hat{y}_{\text{score}} \ge 70.0\% \text{ AND } P(\text{High Risk}) < 0.20
\end{cases}$$

Furthermore, institutional overrides configured in `risk_thresholds` allow specific departments or rigorous courses (e.g., Advanced Calculus CS301) to heighten the high-risk threshold from $50\%$ to $55\%$ or $60\%$.

---

## 7. Model Serialization & Live Inference Pipeline

1. **Artifact Storage:**
   - Serialized pipelines are stored in `trained_models/` via `joblib`:
     - `active_preprocessor.joblib`: Serialized ColumnTransformer.
     - `active_classifier.joblib`: Serialized production classifier.
     - `active_regressor.joblib`: Serialized score regressor.
     - Versioned snapshots (`classifier_v1.0.0.joblib`).
2. **Runtime Inference Workflow:**
   - When a user requests prediction for a student-course pair, `prediction_service.py` executes an optimized SQL join across `students`, `enrollments`, `marks`, and `attendance_records`.
   - Live metrics (computed attendance percentage, midterm assessment scores, past academic history) are extracted into an inference dictionary.
   - The preprocessing pipeline normalizes the features, the classifier outputs risk probabilities $[P_{\text{low}}, P_{\text{med}}, P_{\text{high}}]$, and the regressor forecasts the predicted final score.
   - Significant contributing risk factors (e.g., "Attendance (62.5%) below 75% threshold", "Midterm mark (38.0%) below passing standard") are generated and returned for immediate faculty review.
   - The result is persisted in `predictions` and logged in `prediction_runs`.
