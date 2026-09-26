# 🧠 AI-Powered Process Scheduling

An intelligent CPU scheduling simulator using traditional algorithms and advanced Machine Learning (ML) + Reinforcement Learning (RL) techniques.

---

## 🎯 Project Objective

To build an **AI-powered CPU scheduler** that intelligently chooses the best process to run, aiming to outperform traditional scheduling algorithms like FCFS, SJF, and Round Robin. The goal is to reduce CPU idle time, minimize waiting time, and optimize throughput using ML and RL.



---

## 🧩 End-to-End System Design

### 🔷 Frontend
- **Modern UI**: Completely redesigned interface featuring Glassmorphism, sleek dark mode aesthetics, and smooth micro-animations.
- Input process details: Arrival Time, Burst Time, Priority, etc.
- Select scheduler type: `FCFS`, `SJF`, `Round Robin`, `ML-based`, or `RL-based`.

### 🔶 Backend
- Receives process list and selected scheduler.
- Runs selected scheduling algorithm.
- Returns scheduled process order and performance metrics.

### 📊 Output
- Displays a Gantt Chart or Process Table.
- Shows key metrics:
  - CPU Utilization
  - Average Waiting Time
  - Turnaround Time
  - Throughput
  - RL Rewards

---

## ⚙️ Scheduling Techniques

### 🔁 Traditional Algorithms
- FCFS (First-Come First-Serve)
- SJF (Shortest Job First)
- Round Robin
- Priority Scheduling

These serve as baselines for comparing the performance of AI-based scheduling.

---

## 🤖 AI-Enhanced Scheduling

### 🔍 ML (Machine Learning) for Burst Time Prediction
**Models Evaluated:**
- ✅ `Random Forest` (Best performer)
- ❌ `Linear Regression` (Overfit)
- ❌ `XGBoost` (Underperformed)

**Feature Importance:**
- `io_write_bytes`, `num_ctx_switches_voluntary`, and `cpu_percent`

**Random Forest Results:**
- MAE: 0.0304
- MSE: 0.0815
- R²: 1.0000

### 🧠 RL (Reinforcement Learning) for Process Scheduling

#### 🔁 Problem Modeled As:
- **State**: `[predicted_burst_time, waiting_time, queue_length, progress]`
- **Actions**:
  - `0`: Keep current process running
  - `1`: Switch to another process
- **Reward System**:
  - +5: Process completion
  - -0.5: Context switch
  - -0.1 per waiting process per step
  - Bonus: Efficient total completion
  - Penalty: Long idle/wait times

---

## 🧪 RL Training Setup & Results

### 🧮 Environment:
- Simulates CPU behavior with process queue, arrival/burst times, and priorities.
- Supports learning via trial-and-error (Deep Q-Learning, PPO).

### 🔄 From DQN to PPO:
- Initially used Deep Q-Network (DQN).
- Switched to **Proximal Policy Optimization (PPO)** for better performance in continuous state spaces.

**PPO Parameters:**
- Learning rate: 0.0001
- Discount (γ): 0.99
- Batch size: 32
- Steps per update: 1024

### 📈 Training Improvements:
| Metric             | Before     | After (PPO) |
|--------------------|------------|-------------|
| Success Rate       | 15–23%     | 26–44%      |
| Avg. Reward        | 0.10–0.16  | 0.27–0.41   |
| Throughput         | 0.15–0.23  | 0.26–0.44   |
| Completion Time    | 0.21–0.29  | 0.42–0.62   |

**Changes Made:**
- Learning rate ↓
- Batch size ↑
- Memory size ↑
- Exploration decay slowed
- Frequent target updates

---

## 🧪 Evaluation Episodes

| Episode | Total Reward | Avg. Waiting Time | Completion Time | Processes Completed |
|---------|--------------|-------------------|------------------|----------------------|
| 1       | -44.60       | 88.17             | 233              | 12/12                |
| 2       | 85.00        | 23.57             | 99               | 7/7                  |
| 5       | -60.20       | 95.09             | 229              | 11/11                |
| 10      | 114.40       | 8.50              | 64               | 8/8                  |
| ...     | ...          | ...               | ...              | ...                  |

> Observation: Reward and throughput consistently improve over episodes, showing the RL model is learning effectively.

---

## 🧠 Hybrid AI Model (ML + RL)

- Use ML (`Random Forest`) to **predict burst time**
- Feed predictions to the **RL scheduler**
- Improvement:
  - Without ML: Avg. reward = **20.34**
  - With ML: Avg. reward = **22.39**

> Using ML-enhanced burst time improves scheduling outcomes slightly and leads to smoother learning.

---

## 🧪 Final Test Case

**User Input:**
P1: 0, 10, ...
P2: 1, 8, ...


**Results:**
- Avg. Waiting Time: `18.00`
- Avg. Response Time: `0.25`
- Total Reward: `19.38`

---

## 📉 Challenges Faced

- Model performs well when all processes arrive at time 0.
- In realistic scenarios (varied arrival times), performance drops.
- Inconsistencies across runs suggest the need for better generalization.
- Waiting time sometimes shows incorrect values (needs metric debugging).

---

## 🚀 Future Enhancements

- Add **Batch Normalization** to stabilize training.
- Expand **feature set** for smarter decisions.
- Tune RL hyperparameters using grid search.
- Implement **priority-aware RL policies**.
- Add **starvation prevention mechanisms**.
- Extend to multi-core CPU simulations.

---


---

## 📚 Technologies Used

- **Frontend**: HTML5, Modern CSS (Glassmorphism, Animations), Bootstrap 5, JavaScript
- **Backend**: Python (Flask)
- **AI/ML**: Scikit-learn, PyTorch, PPO (Proximal Policy Optimization)
- **Visualization**: Matplotlib (for analysis & visualization)

---

## 📌 Conclusion

This project showcases a powerful integration of traditional scheduling principles with modern AI techniques. While ML and RL models enhance scheduling decisions, their success depends on well-designed environments and reward structures. Ongoing improvements aim to create a generalized, intelligent scheduler for real-world operating systems.

---

## 🔗 GitHub Repo

[👉 View Source on GitHub](https://github.com/AjayKumarOnly/Ai-driven-Process-Management-System-)

---

