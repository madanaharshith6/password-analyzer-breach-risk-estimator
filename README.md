\# Password Analyzer \& Breach Risk Estimator



A hybrid password security analysis application that evaluates password strength using deterministic security rules, machine learning, and real-time breach screening.



\## Key Features



\- \*\*Password Strength Analysis:\*\* Evaluates password complexity and security characteristics.

\- \*\*Rule-Based Engine:\*\* Uses deterministic security rules to identify weak password patterns.

\- \*\*Machine Learning:\*\* Uses a supervised ML model with 20 extracted features.

\- \*\*Breach Detection:\*\* Uses the Have I Been Pwned Pwned Passwords API with SHA-1 k-anonymity.

\- \*\*Hybrid Evaluation:\*\* Combines rule-based and ML assessments.

\- \*\*Security Recommendations:\*\* Provides suggestions to improve password security.

\- \*\*Password Manager:\*\* Provides password-management functionality.

\- \*\*Audit History:\*\* Records anonymized audit metadata using SQLite.

\- \*\*Model Performance:\*\* Includes model evaluation and performance visualizations.

\- \*\*Automated Tests:\*\* Includes tests for security rules, breach checking, ML, and other components.



\## Technology Stack



\- Python

\- Streamlit

\- Scikit-learn

\- Pandas

\- NumPy

\- SQLite

\- Joblib

\- Have I Been Pwned API

\- Pytest



\## Project Structure



```text

password-analyzer-breach-risk-estimator/

│

├── password\_strength\_estimator/

│   ├── app.py

│   ├── config.py

│   ├── requirements.txt

│   ├── database/

│   ├── machine\_learning/

│   ├── modules/

│   ├── pages/

│   ├── tests/

│   └── assets/

│

└── README.md

```



\## Installation and Setup



1\. Clone the repository:



```bash

git clone https://github.com/madanaharshith6/password-analyzer-breach-risk-estimator.git

```



2\. Navigate to the application directory:



```bash

cd password-analyzer-breach-risk-estimator/password\_strength\_estimator

```



3\. Create a virtual environment:



```bash

python -m venv venv

```



4\. Activate the environment on Windows:



```bash

venv\\Scripts\\activate

```



5\. Install dependencies:



```bash

pip install -r requirements.txt

```



6\. Run the application:



```bash

streamlit run app.py

```



\## Running Tests



```bash

pytest -v

```



\## Security Note



The breach-checking feature uses SHA-1 k-anonymity to avoid sending the complete password to the breach-checking service. Never commit real passwords, API secrets, environment files, or private database records to GitHub.



\## Project Purpose



This project demonstrates the application of cybersecurity concepts, machine learning, password analysis, and secure software development practices in an interactive application.



\## Author



\*\*Madana Komal Siva Sai Harshith\*\*



GitHub: \[madanaharshith6](https://github.com/madanaharshith6)



Repository: \[Password Analyzer \& Breach Risk Estimator](https://github.com/madanaharshith6/password-analyzer-breach-risk-estimator)

