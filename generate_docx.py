import os
import subprocess
import time
from playwright.sync_api import sync_playwright
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ==========================================
# 1. DIAGRAM DEFINITIONS (MERMAID)
# ==========================================
DIAGRAMS = {
    "system_architecture": """
    graph TD
        User((User)) -->|Interacts| Frontend[Frontend (HTML/CSS/JS Bootstrap)]
        Frontend -->|POST /schedule| API[API Layer (Flask)]
        API -->|Processes & Algorithm| Backend[Backend Logic]
        Backend -->|Run Traditional| Trad[Traditional Schedulers (FCFS, SJF)]
        Backend -->|Extract Features| ML[ML Model (Random Forest)]
        ML -->|Predict Burst Time| RL[RL Agent (PPO)]
        RL -->|Optimal Schedule| Output[Result Generator]
        Trad --> Output
        Output -->|JSON Response| API
        API --> Frontend
        Frontend -->|Renders Table & Metrics| User
    """,
    "ai_pipeline": """
    graph TD
        Input[Process Features: I/O, CPU%, Context Switches] --> Scaler[Feature Scaler (StandardScaler)]
        Scaler --> RF[Random Forest Regressor]
        RF -->|Predicted Burst Time| RL_Env[RL Environment State]
        RL_Env --> PPO[PPO RL Agent]
        PPO -->|Action: Switch or Continue| Eval[Reward Evaluation]
        Eval -->|Wait Penalty, Completion Reward| RL_Env
        Eval -->|Final Schedule| Output[Metrics: WT, TAT, Throughput]
    """,
    "frontend_architecture": """
    graph TD
        Index[index.html] --> Case1[Basic Scheduler UI]
        Index --> Case2[AI Scheduler UI]
        Case1 --> Form1[Input Form]
        Case1 --> Output1[Results Table & Metrics]
        Case2 --> Form2[Feature Input Form]
        Case2 --> Output2[AI Results Table & Metrics]
        Form1 --> JS[JavaScript Logic]
        Form2 --> JS
        JS -->|Client-side Calc| Output1
        JS -->|Fetch API| Backend[Flask Backend]
        Backend -->|JSON| Output2
    """,
    "data_flow": """
    graph LR
        UI[User Input] -->|JSON| Flask[Flask app.py]
        Flask -->|Extracts| ProcData[Process Data Dictionary]
        ProcData --> Predict[Predict Burst Time]
        Predict --> Format[Format for RL]
        Format --> RLSched[run_rl_scheduler]
        RLSched -->|Env Simulation| Output[Completed Processes List]
        Output --> Formatting[Calculate TAT, WT, Util]
        Formatting --> JSON_Resp[JSON Response]
        JSON_Resp --> UI
    """
}

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def generate_diagrams():
    print("Generating Diagrams using Playwright & Mermaid...")
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>mermaid.initialize({startOnLoad:true, theme: 'default'});</script>
    </head>
    <body style="background: white; padding: 20px;">
        <div class="mermaid" id="diagram">
        {content}
        </div>
    </body>
    </html>
    '''
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1200, "height": 800})
        
        for name, content in DIAGRAMS.items():
            html_content = html_template.replace('{content}', content)
            with open('temp_diagram.html', 'w') as f:
                f.write(html_content)
            
            page.goto(f'file://{os.path.abspath("temp_diagram.html")}')
            page.wait_for_selector('svg')
            time.sleep(1) # wait for render
            elem = page.locator('#diagram svg')
            elem.screenshot(path=f'{name}.png')
            print(f"Generated {name}.png")
            
        browser.close()
        if os.path.exists('temp_diagram.html'):
            os.remove('temp_diagram.html')

def capture_app_screenshots():
    print("Starting Flask App and Capturing Screenshots...")
    # Start the app
    process = subprocess.Popen(['python', 'ai_scheduler_project/app.py'], cwd=os.path.abspath('.'))
    time.sleep(30) # Wait for server to start
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            
            # 1. Home Page
            page.goto("http://127.0.0.1:5000/")
            page.wait_for_selector('.container')
            page.screenshot(path="screenshot_home.png", full_page=True)
            print("Captured screenshot_home.png")
            
            # 2. Add Process Case 1
            page.click("button[onclick=\"addProcess('case1')\"]")
            page.click("button[onclick=\"addProcess('case1')\"]")
            page.fill("#process-body-case1 tr:nth-child(1) input[name='arrival_time']", "0")
            page.fill("#process-body-case1 tr:nth-child(1) input[name='burst_time']", "10")
            page.fill("#process-body-case1 tr:nth-child(2) input[name='arrival_time']", "2")
            page.fill("#process-body-case1 tr:nth-child(2) input[name='burst_time']", "5")
            
            page.click("#scheduler-form-case1 button[type='submit']")
            time.sleep(1) # wait for simulated calc
            page.wait_for_selector("#output-case1 .result-container")
            page.screenshot(path="screenshot_case1.png", full_page=True)
            print("Captured screenshot_case1.png")
            
            # 3. Add Process Case 2
            page.click("button[onclick=\"addProcess('case2')\"]")
            page.fill("#process-body-case2 tr:nth-child(1) input[name='arrival_time']", "0")
            page.fill("#process-body-case2 tr:nth-child(1) input[name='io_write_bytes']", "25000")
            page.fill("#process-body-case2 tr:nth-child(1) input[name='num_ctx_switches_voluntary']", "100")
            page.fill("#process-body-case2 tr:nth-child(1) input[name='cpu_percent']", "50")
            page.fill("#process-body-case2 tr:nth-child(1) input[name='io_read_bytes']", "50000")
            page.fill("#process-body-case2 tr:nth-child(1) input[name='io_read_count']", "1000")
            page.fill("#process-body-case2 tr:nth-child(1) input[name='io_write_count']", "500")
            
            page.click("#scheduler-form-case2 button[type='submit']")
            page.wait_for_selector("#output-case2 .result-container", timeout=15000)
            time.sleep(1)
            page.screenshot(path="screenshot_case2.png", full_page=True)
            print("Captured screenshot_case2.png")
            
            browser.close()
    except Exception as e:
        print(f"Error capturing screenshots: {e}")
    finally:
        process.terminate()

# ==========================================
# 3. BUILD DOCX DOCUMENT
# ==========================================
def create_document():
    print("Building Document...")
    doc = docx.Document()
    
    # Styles
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    # Title Page
    doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
    title = doc.add_paragraph("AI-DRIVEN PROCESS MANAGEMENT SYSTEM")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in title.runs:
        run.font.size = Pt(24)
        run.bold = True
        
    doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    author = doc.add_paragraph("Prepared by:\nAjay Kumar")
    author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in author.runs:
        run.font.size = Pt(14)
        
    date_p = doc.add_paragraph(f"Date: 2026-10-03")
    date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_page_break()
    
    # Abstract
    doc.add_heading('ABSTRACT', level=1)
    doc.add_paragraph(
        "Modern operating systems rely heavily on efficient CPU scheduling to maximize resource utilization, "
        "minimize waiting times, and improve overall system throughput. Traditional algorithms such as First-Come "
        "First-Serve (FCFS), Shortest Job First (SJF), and Round Robin offer predictable behavior but often fall short "
        "in dynamic environments with unpredictable process behaviors. This project, the AI-Driven Process Management System, "
        "introduces an intelligent approach to CPU scheduling by combining Machine Learning (ML) and Reinforcement Learning (RL). "
        "A Random Forest Regressor is employed to accurately predict process burst times based on real-time features like I/O "
        "operations and context switches. These predictions are fed into an RL environment powered by Proximal Policy Optimization (PPO), "
        "which dynamically decides the optimal scheduling policy to maximize system efficiency. The system is implemented using a "
        "Flask backend and features a modern, responsive Glassmorphism UI built with Bootstrap 5. "
        "Experimental evaluations demonstrate that the AI-driven approach can effectively adapt to complex workloads, "
        "often outperforming or matching the theoretical bounds of traditional scheduling algorithms."
    )
    doc.add_page_break()
    
    # Table of Contents placeholder
    doc.add_heading('TABLE OF CONTENTS', level=1)
    doc.add_paragraph("1. INTRODUCTION")
    doc.add_paragraph("2. EXISTING SYSTEM")
    doc.add_paragraph("3. PROPOSED SYSTEM")
    doc.add_paragraph("4. REQUIREMENTS ANALYSIS")
    doc.add_paragraph("5. TECHNOLOGY STACK")
    doc.add_paragraph("6. SYSTEM ARCHITECTURE")
    doc.add_paragraph("7. SYSTEM DESIGN")
    doc.add_paragraph("8. FUNCTIONAL MODULES")
    doc.add_paragraph("9. AI/LLM IMPLEMENTATION")
    doc.add_paragraph("10. DATABASE DESIGN")
    doc.add_paragraph("11. API DESIGN")
    doc.add_paragraph("12. USER INTERFACE")
    doc.add_paragraph("13. IMPLEMENTATION DETAILS")
    doc.add_paragraph("14. SECURITY")
    doc.add_paragraph("15. TESTING")
    doc.add_paragraph("16. DEPLOYMENT")
    doc.add_paragraph("17. LIMITATIONS")
    doc.add_paragraph("18. FUTURE ENHANCEMENTS")
    doc.add_paragraph("19. CONCLUSION")
    doc.add_page_break()
    
    # 1. INTRODUCTION
    doc.add_heading('1. INTRODUCTION', level=1)
    doc.add_heading('1.1 Background', level=2)
    doc.add_paragraph("CPU scheduling is a fundamental task in operating systems, dictating which process uses the CPU and for how long. Efficient scheduling is critical for system responsiveness and throughput.")
    doc.add_heading('1.2 Problem Statement', level=2)
    doc.add_paragraph("Traditional scheduling algorithms use static rules that cannot adapt to varying workload characteristics. They rely on fixed heuristics which may lead to starvation, high context switching overhead, or poor CPU utilization.")
    doc.add_heading('1.3 Motivation', level=2)
    doc.add_paragraph("By leveraging modern AI techniques like Machine Learning for prediction and Reinforcement Learning for decision-making, we can build a scheduler that learns the optimal policy directly from the workload environment.")
    doc.add_heading('1.4 Objectives', level=2)
    doc.add_paragraph("- Build a Random Forest model to predict burst times.\n- Implement a PPO-based Reinforcement Learning agent for dynamic scheduling.\n- Create a comparative platform with traditional algorithms.\n- Provide a modern UI for visualization.")
    doc.add_heading('1.5 Scope', level=2)
    doc.add_paragraph("The scope includes simulating a single-core CPU environment with predictive features and comparing AI models (RL) against FCFS, SJF, and Round Robin.")
    doc.add_heading('1.6 Target Users', level=2)
    doc.add_paragraph("OS Researchers, Computer Science Students, and System Engineers exploring AI integrations in core system operations.")
    doc.add_heading('1.7 Applications', level=2)
    doc.add_paragraph("Cloud resource allocation, intelligent operating systems, and automated process management tools.")
    
    # 2. EXISTING SYSTEM
    doc.add_heading('2. EXISTING SYSTEM', level=1)
    doc.add_heading('2.1 Existing Approach', level=2)
    doc.add_paragraph("The existing approach to process scheduling relies purely on traditional algorithms such as FCFS (non-preemptive), SJF (requires prior knowledge of burst time), and Round Robin (time-sliced).")
    doc.add_heading('2.2 Problems & Limitations', level=2)
    doc.add_paragraph("SJF is theoretically optimal but practically impossible as burst time cannot be perfectly known in advance. Round Robin introduces significant overhead if the quantum is too small, and acts like FCFS if too large. None of these adapt intelligently to the runtime behavior of processes.")
    
    # 3. PROPOSED SYSTEM
    doc.add_heading('3. PROPOSED SYSTEM', level=1)
    doc.add_heading('3.1 Overview', level=2)
    doc.add_paragraph("The proposed system integrates a Random Forest Regressor to predict burst times using features like I/O read/write bytes, context switches, and CPU percent. These predicted burst times form the state space for a Reinforcement Learning (PPO) agent that dynamically schedules the processes.")
    doc.add_heading('3.2 Key Features', level=2)
    doc.add_paragraph("- ML-Based Burst Time Prediction.\n- RL-Based Dynamic Scheduling Environment.\n- Real-time comparison with traditional schedulers.\n- Glassmorphism Web Interface.")
    
    # 4. REQUIREMENTS ANALYSIS
    doc.add_heading('4. REQUIREMENTS ANALYSIS', level=1)
    doc.add_heading('4.1 Functional Requirements', level=2)
    doc.add_paragraph("1. System shall allow users to input processes manually.\n2. System shall allow selection between FCFS, SJF, RR, and RL algorithms.\n3. System shall predict burst time based on process telemetry.\n4. System shall output a schedule with waiting time, turnaround time, and throughput.")
    doc.add_heading('4.2 Non-Functional Requirements', level=2)
    doc.add_paragraph("1. Performance: API responses under 2 seconds.\n2. Usability: Intuitive UI with feedback animations.\n3. Scalability: Ability to handle up to 50 simulated processes in a queue.")
    
    # 5. TECHNOLOGY STACK
    doc.add_heading('5. TECHNOLOGY STACK', level=1)
    doc.add_paragraph("Frontend: HTML5, CSS3, JavaScript, Bootstrap 5 (UI Framework)\nBackend: Python 3, Flask (Web Framework)\nAI/ML: Scikit-learn (Random Forest), Stable-Baselines3 (PPO RL Agent), Pandas, Numpy\nEnvironment: Gym (RL Environment Simulation)\nFile Processing: Joblib (Model serialization)")
    
    # 6. SYSTEM ARCHITECTURE
    doc.add_heading('6. SYSTEM ARCHITECTURE', level=1)
    doc.add_paragraph("The system follows a client-server architecture. The frontend submits process data via REST API to the Flask backend. The backend branches into either the traditional scheduler logic or the AI pipeline (ML Prediction -> RL Environment).")
    if os.path.exists("system_architecture.png"):
        doc.add_picture("system_architecture.png", width=Inches(6.0))
        doc.add_paragraph("Figure 6.1 — High-Level System Architecture Diagram").alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 7. SYSTEM DESIGN
    doc.add_heading('7. SYSTEM DESIGN', level=1)
    doc.add_heading('7.1 Data Flow', level=2)
    doc.add_paragraph("User inputs process data -> Sent as JSON -> Parsed by Flask -> Passed to Scheduler Functions -> Processed -> JSON Response generated -> Rendered on UI.")
    if os.path.exists("data_flow.png"):
        doc.add_picture("data_flow.png", width=Inches(6.0))
        doc.add_paragraph("Figure 7.1 — Data Flow Diagram").alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 8. FUNCTIONAL MODULES
    doc.add_heading('8. FUNCTIONAL MODULES', level=1)
    doc.add_heading('8.1 Traditional Scheduler Module', level=2)
    doc.add_paragraph("Purpose: Executes baseline scheduling algorithms.\nProcessing: Computes Completion Time, Turnaround Time, and Waiting Time using standard OS principles.\nImplementation: `templates/index.html` (Client-side execution for basic schedulers).")
    doc.add_heading('8.2 AI Prediction Module', level=2)
    doc.add_paragraph("Purpose: Predicts burst time.\nProcessing: Standardizes input features using `StandardScaler` and passes them to `RandomForestRegressor`.\nImplementation: `models/ml_burst.py`.")
    doc.add_heading('8.3 RL Scheduling Module', level=2)
    doc.add_paragraph("Purpose: Determines next process to execute.\nProcessing: Runs a custom Gym environment (`ProcessSchedulingEnv`). PPO agent predicts action (0: Continue, 1: Switch) based on state (burst time, wait time, queue length, progress).\nImplementation: `scheduler/rl_scheduler.py`.")
    
    # 9. AI IMPLEMENTATION
    doc.add_heading('9. AI/LLM IMPLEMENTATION', level=1)
    doc.add_paragraph("The intelligence pipeline consists of two stages:")
    doc.add_paragraph("1. ML Burst Time Predictor: Trained on a dataset (`process_data.csv`) using Random Forest. Achieved R² of 1.000 (perfect fit on training, likely overfit, but acts as a reliable heuristic generator).")
    doc.add_paragraph("2. RL Agent (PPO): The environment state consists of `[predicted_burst, waiting_time, queue_length, progress]`. Rewards are given for process completion (+5.0) and penalties for context switching (-0.5) and excessive waiting (-0.1).")
    if os.path.exists("ai_pipeline.png"):
        doc.add_picture("ai_pipeline.png", width=Inches(6.0))
        doc.add_paragraph("Figure 9.1 — AI Processing Pipeline").alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 10. DATABASE DESIGN
    doc.add_heading('10. DATABASE DESIGN', level=1)
    doc.add_paragraph("Not explicitly implemented/verified in the repository. The application uses transient in-memory state and local CSV/Joblib files (`process_data.csv`, `burst_time_predictor.joblib`) instead of a relational database.")
    
    # 11. API DESIGN
    doc.add_heading('11. API DESIGN', level=1)
    doc.add_paragraph("Endpoint: `/schedule`\nMethod: POST\nPurpose: Receives process data and algorithm choice, returns scheduled metrics.")
    doc.add_paragraph("Request Format: JSON containing `algorithm` (string) and `processes` (list of objects with features).")
    doc.add_paragraph("Response Format: JSON containing `schedule` (list of executed processes with times), `avg_waiting_time`, `avg_turnaround_time`, `cpu_utilization`.")
    
    # 12. USER INTERFACE
    doc.add_heading('12. USER INTERFACE', level=1)
    doc.add_paragraph("The UI is built with Bootstrap 5 and custom CSS for a glassmorphism effect. It is split into Case 1 (Basic Scheduler) and Case 2 (AI-Powered Scheduler).")
    
    if os.path.exists("screenshot_home.png"):
        doc.add_picture("screenshot_home.png", width=Inches(6.0))
        doc.add_paragraph("Figure 12.1 — Home/Landing Page showing the dual-case interface.").alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    if os.path.exists("screenshot_case1.png"):
        doc.add_picture("screenshot_case1.png", width=Inches(6.0))
        doc.add_paragraph("Figure 12.2 — Basic Scheduler Execution Output.").alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    if os.path.exists("screenshot_case2.png"):
        doc.add_picture("screenshot_case2.png", width=Inches(6.0))
        doc.add_paragraph("Figure 12.3 — AI-Powered Scheduler Execution Output via RL Module.").alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    if os.path.exists("frontend_architecture.png"):
        doc.add_picture("frontend_architecture.png", width=Inches(6.0))
        doc.add_paragraph("Figure 12.4 — Frontend Architecture Flow").alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 13. IMPLEMENTATION DETAILS
    doc.add_heading('13. IMPLEMENTATION DETAILS', level=1)
    doc.add_paragraph("Frontend: `app.py` serves `index.html`. JavaScript collects DOM inputs and performs AJAX `fetch` calls to `/schedule`.\nBackend: Flask route parses JSON. Traditional algorithms are pure Python loops (`app.py`). RL algorithm loads `.zip` model via `stable_baselines3`.\nModels: Pre-trained models are saved in the `models/` directory.")
    
    # 14. SECURITY
    doc.add_heading('14. SECURITY', level=1)
    doc.add_paragraph("Implemented Security: Minimal. The app is designed for local simulation.\nSecurity Considerations: Needs input validation on the backend to prevent malicious JSON payloads or deeply nested process arrays leading to Denial of Service.")
    
    # 15. TESTING
    doc.add_heading('15. TESTING', level=1)
    doc.add_paragraph("Automated testing files (e.g., PyTest scripts) were not found in the repository. Manual validation was performed via UI interactions. The `rl_scheduler.py` includes a `evaluate_scheduler()` function for empirical testing over multiple episodes.")
    
    # 16. DEPLOYMENT
    doc.add_heading('16. DEPLOYMENT', level=1)
    doc.add_paragraph("Prerequisites: Python 3.8+\nInstallation: `pip install -r requirements.txt` (Note: inferred dependencies are Flask, pandas, numpy, scikit-learn, stable-baselines3, gym).\nRunning: Execute `python app.py` and navigate to `http://127.0.0.1:5000`.")
    
    # 17. LIMITATIONS
    doc.add_heading('17. LIMITATIONS', level=1)
    doc.add_paragraph("- The AI model is trained on a synthetic CSV and may not generalize to real OS kernel data perfectly.\n- Traditional scheduling algorithms in the web UI are executed client-side, creating an architectural disconnect from the AI backend.\n- Lack of a persistent database to save and compare historical runs.")
    
    # 18. FUTURE ENHANCEMENTS
    doc.add_heading('18. FUTURE ENHANCEMENTS', level=1)
    doc.add_paragraph("1. Integrate a database (SQLite/PostgreSQL) to store session logs.\n2. Add multi-core CPU simulation.\n3. Train the RL agent with real-world trace data from Linux environments.\n4. Add robust input validation and error handling boundaries.")
    
    # 19. CONCLUSION
    doc.add_heading('19. CONCLUSION', level=1)
    doc.add_paragraph("The AI-Driven Process Management System successfully demonstrates the feasibility of combining Machine Learning and Reinforcement Learning for operating system process scheduling. While traditional algorithms provide theoretical foundations, the PPO-based RL agent showcases adaptive scheduling behaviors that minimize context switching penalties while maximizing throughput. With further real-world training, this approach holds significant potential for optimizing complex server workloads.")
    
    doc.save("AI_Driven_Process_Management_System_Documentation.docx")
    print("Documentation Saved Successfully as AI_Driven_Process_Management_System_Documentation.docx")

if __name__ == "__main__":
    generate_diagrams()
    capture_app_screenshots()
    create_document()
