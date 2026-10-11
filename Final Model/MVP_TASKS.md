# MVP: Quantum Teleportation Project - Phase 2

## Overview
This MVP outlines the core development tasks for Phase 2 of the Quantum Teleportation Project. The objective is to build a machine learning model that predicts secure key rates and transmission metrics based on quantum protocol parameters.

---

## Task 1: Custom Model Development

**Objective:** Create and train a custom ML model that predicts secure key rates and transmission efficiency.

**Inputs:**
- Architecture (quantum protocol type)
- Distance (transmission distance)
- Noise Factor (environmental noise level)

**Outputs:**
- Secure Key Rate (along with the protocol name)
- Transmission efficiency
<!-- - Single-qubit fidelity
- Two-qubit fidelity
- T1, T2 coherence times -->

**Requirements:**
- [ ] Analyze existing dataset(s) in `/data/` directory
- [ ] Implement feature engineering for quantum parameters
- [ ] Design model architecture suitable for quantum metrics prediction
- [ ] Train model on available QKD protocol data (BB84, BBM92, SARG04, Six-State, Decoy-BB84, E91, B92, AB-QKD, DS6-QKD, EEPM-QKD)
- [ ] Validate model performance against test sets
- [ ] Save trained model artifacts for inference

**Deliverables:**
- Trained model checkpoint
- Feature preprocessing pipeline
- Model evaluation metrics and accuracy report

---

## Task 2: Testing Script Development

**Objective:** Create a comprehensive testing suite to validate model predictions and ensure reliability.

**Requirements:**
- [ ] Load trained model and preprocessing pipeline
- [ ] Implement test cases for various input scenarios:
  - Different QKD protocols (BB84, BBM92, SARG04, Six-State, Decoy-BB84, E91, B92, AB-QKD, DS6-QKD, EEPM-QKD)
  - Various distance ranges
  - Multiple noise factor values
- [ ] Validate output format and ranges
- [ ] Compare predictions with expected baselines
- [ ] Generate test report with pass/fail statistics
- [ ] Create visualization of predictions vs. actual data

**Test Coverage:**
- Edge cases (minimum/maximum noise, extreme distances)
- Multiple protocol validation
- Output consistency checks
- Inference performance benchmarking

**Deliverables:**
- `test_model.py` - Main testing script
- Test results report with performance metrics
- Validation plots and visualizations

---

## Data Sources
- `/data/bbm92_*.csv` - BBM92 protocol data
- `/data/decoybb84_*.csv` - Decoy BB84 protocol data
- `/data/qkd_final_*.csv` - QKD final dataset
- `/data/sarg04_*.csv` - SARG04 protocol data
- `/data/sixstate_*.csv` - Six-State protocol data
- `/data/novel_protocols_*.csv` - Novel protocol variations

---

## Success Criteria
1. ✓ Model achieves >90% accuracy on validation set
2. ✓ All test cases pass with acceptable error margins
3. ✓ Predictions fall within physically plausible ranges
4. ✓ Model can be deployed for inference
5. ✓ Complete documentation and reproducibility

---

## Notes
- Ensure reproducibility with fixed random seeds
- Document all hyperparameters and design decisions
- Create modular code for easy maintenance and extension
- Include comprehensive error handling and logging
