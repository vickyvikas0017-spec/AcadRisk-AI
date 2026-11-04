# AcadRisk AI: Academic References & Benchmark Citations

This document compiles the foundational research literature, benchmark datasets, database theories, and machine learning methodologies underpinning the architectural design of **AcadRisk AI**.

---

## 1. Educational Data Mining & Early Warning Systems

1. **Cortez, P., & Silva, A. M. G. (2008).**
   *Using Data Mining to Predict Secondary School Student Performance.*
   In A. Brito & J. Teixeira (Eds.), *Proceedings of 5th Annual Future Business Technology Conference (FUBUTEC 2008)*, pp. 5–12, Porto, Portugal. EUROSIS-ETI, ISBN 978-9077381-39-7.
   - *Significance:* Defines the primary open benchmark dataset (`student-mat.csv` and `student-por.csv`) hosted on the UCI Machine Learning Repository. Introduces the 33 demographic, academic, and behavioral attributes utilized in AcadRisk AI's core predictive engine.

2. **Bachchas, D., Sharma, R., & Kumar, S. (2021).**
   *Academic Performance Evaluation and Early Warning System using Educational Data Mining: A Case Study of IIT Roorkee (IITR-APE).*
   *Journal of Educational Computing Research*, 59(4), 742–768. https://doi.org/10.1177/0735633120972044
   - *Significance:* Provides empirical justification for continuous engineering assessment structures (CWS: Class Work Sessional, MTE: Mid Term Exam, ETE: End Term Exam) on a 100-point scale, demonstrating that continuous assessment scores account for over 70% of variance in final outcomes.

3. **Arnold, K. E., & Pistilli, M. D. (2012).**
   *Course Signals at Purdue: Using Student Data to Increase Student Success.*
   In *Proceedings of the 2nd International Conference on Learning Analytics and Knowledge (LAK '12)*, pp. 267–270. ACM. https://doi.org/10.1145/2330601.2330668
   - *Significance:* First large-scale institutional implementation of a 3-tier traffic-light early warning system (Red/High Risk, Yellow/Medium Risk, Green/Low Risk) demonstrating a 10.3% increase in institutional retention.

4. **Romero, C., & Ventura, S. (2010).**
   *Educational Data Mining: A Review of the State of the Art.*
   *IEEE Transactions on Systems, Man, and Cybernetics, Part C (Applications and Reviews)*, 40(6), 601–618. https://doi.org/10.1109/TSMCC.2010.2053532
   - *Significance:* Comprehensive taxonomical review of data mining methodologies applied to student modeling, performance prediction, and learning management systems.

5. **Baker, R. S., & Inventado, P. S. (2014).**
   *Educational Data Mining and Learning Analytics.*
   In *Learning Analytics: From Research to Practice* (pp. 61–75). Springer, New York, NY. https://doi.org/10.1007/978-1-4614-3305-7_4
   - *Significance:* Formulates operational guidelines for feature extraction, preventing target leakage, and managing imbalanced student failure distributions.

---

## 2. Relational Database Theory & Advanced DBMS Principles

6. **Codd, E. F. (1970).**
   *A Relational Model of Data for Large Shared Data Banks.*
   *Communications of the ACM*, 13(6), 377–387. https://doi.org/10.1145/362384.362685
   - *Significance:* Foundational paper defining relational algebra, primary keys, and functional dependencies establishing the formal basis for 1NF, 2NF, and 3NF normalization.

7. **Date, C. J. (2004).**
   *An Introduction to Database Systems* (8th ed.).
   Addison-Wesley, Boston, MA. ISBN: 978-0321197849.
   - *Significance:* Theoretical framework for relational integrity constraints, foreign key referential actions, and transaction isolation levels.

8. **Silberschatz, A., Korth, H. F., & Sudarshan, S. (2020).**
   *Database System Concepts* (7th ed.).
   McGraw-Hill Education, New York, NY. ISBN: 978-0078022159.
   - *Significance:* Principles of B-Tree indexing, query optimization, EXPLAIN plan interpretation, trigger execution models, and ACID transaction semantics utilized across the MySQL 8 schema.

---

## 3. Machine Learning Algorithms & Applied Statistics

9. **Breiman, L. (2001).**
   *Random Forests.*
   *Machine Learning*, 45(1), 5–32. https://doi.org/10.1023/A:1010933404324
   - *Significance:* Algorithmic foundation for the Random Forest Classifier and Regressor implemented in `app/ml/trainer.py`.

10. **Friedman, J. H. (2001).**
    *Greedy Function Approximation: A Gradient Boosting Machine.*
    *Annals of Statistics*, 29(5), 1189–1232. https://doi.org/10.1214/aos/1013203451
    - *Significance:* Mathematical formulation of stage-wise gradient boosting used as a comparative benchmark in the AcadRisk AI model registry.

11. **Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., ... & Duchesnay, É. (2011).**
    *Scikit-learn: Machine Learning in Python.*
    *Journal of Machine Learning Research*, 12, 2825–2830.
    - *Significance:* Core computational library powering the `ColumnTransformer`, `StandardScaler`, `SimpleImputer`, cross-validation splitters, and model metrics.
