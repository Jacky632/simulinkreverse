/*
 * process_PIConstrained_data.c
 *
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * Code generation for model "process_PIConstrained".
 *
 * Model version              : 1.23
 * Simulink Coder version : 24.1 (R2024a) 19-Nov-2023
 * C source code generated on : Wed Jul  8 14:58:01 2026
 *
 * Target selection: grt.tlc
 * Note: GRT includes extra infrastructure and instrumentation for prototyping
 * Embedded hardware selection: Intel->x86-64 (Windows64)
 * Code generation objective: Debugging
 * Validation result: Not run
 */

#include "process_PIConstrained.h"

/* Block parameters (default storage) */
P_process_PIConstrained_T process_PIConstrained_P = {
  /* Mask Parameter: L2ProportionalGain_gain
   * Referenced by: '<S1>/Slider Gain'
   */
  -14.18,

  /* Expression: 1
   * Referenced by: '<S5>/L2Int'
   */
  1.0,

  /* Expression: 2
   * Referenced by: '<S2>/Saturation'
   */
  2.0,

  /* Expression: 0
   * Referenced by: '<S2>/Saturation'
   */
  0.0,

  /* Expression: 200
   * Referenced by: '<Root>/F1_Step'
   */
  200.0,

  /* Expression: 10
   * Referenced by: '<Root>/F1_Step'
   */
  10.0,

  /* Expression: 10
   * Referenced by: '<Root>/F1_Step'
   */
  10.0,

  /* Expression: 50
   * Referenced by: '<Root>/F3'
   */
  50.0,

  /* Expression: 0.16
   * Referenced by: '<S6>/Gain1'
   */
  0.16,

  /* Expression: 90
   * Referenced by: '<S6>/Constant1'
   */
  90.0,

  /* Expression: 194.7
   * Referenced by: '<Root>/P100'
   */
  194.7,

  /* Expression: 400
   * Referenced by: '<S2>/Saturation2'
   */
  400.0,

  /* Expression: 0
   * Referenced by: '<S2>/Saturation2'
   */
  0.0,

  /* Expression: 0.1538
   * Referenced by: '<S6>/Gain'
   */
  0.1538,

  /* Expression: 25
   * Referenced by: '<S7>/X2Int'
   */
  25.0,

  /* Expression: 0.3126
   * Referenced by: '<S7>/Gain3'
   */
  0.3126,

  /* Expression: 48.43
   * Referenced by: '<S7>/Constant'
   */
  48.43,

  /* Expression: 50.5
   * Referenced by: '<S7>/P2Int'
   */
  50.5,

  /* Expression: 100
   * Referenced by: '<S7>/Saturation1'
   */
  100.0,

  /* Expression: 0
   * Referenced by: '<S7>/Saturation1'
   */
  0.0,

  /* Expression: 0.5616
   * Referenced by: '<S7>/Gain2'
   */
  0.5616,

  /* Expression: 40
   * Referenced by: '<Root>/T1'
   */
  40.0,

  /* Expression: 0.07
   * Referenced by: '<S7>/Gain5'
   */
  0.07,

  /* Expression: 1/38.5
   * Referenced by: '<S7>/Gain6'
   */
  0.025974025974025976,

  /* Expression: 16
   * Referenced by: '<S7>/Saturation'
   */
  16.0,

  /* Expression: 0
   * Referenced by: '<S7>/Saturation'
   */
  0.0,

  /* Expression: 16
   * Referenced by: '<S2>/Saturation4'
   */
  16.0,

  /* Expression: 0
   * Referenced by: '<S2>/Saturation4'
   */
  0.0,

  /* Expression: 2
   * Referenced by: '<Root>/F2'
   */
  2.0,

  /* Expression: 208
   * Referenced by: '<Root>/F200'
   */
  208.0,

  /* Expression: 0
   * Referenced by: '<Root>/FeedbackInt'
   */
  0.0,

  /* Expression: 200
   * Referenced by: '<Root>/L2 Set Point'
   */
  200.0,

  /* Expression: 1
   * Referenced by: '<Root>/L2 Set Point'
   */
  1.0,

  /* Expression: 1
   * Referenced by: '<Root>/L2 Set Point'
   */
  1.0,

  /* Expression: 25
   * Referenced by: '<Root>/T200'
   */
  25.0,

  /* Expression: 1/18.93
   * Referenced by: '<Root>/Ti '
   */
  0.052826201796090863,

  /* Expression: 6.84
   * Referenced by: '<S4>/Constant'
   */
  6.84,

  /* Expression: 2*0.07
   * Referenced by: '<S4>/Constant1'
   */
  0.14,

  /* Expression: 1
   * Referenced by: '<S4>/Constant2'
   */
  1.0,

  /* Expression: 0.507
   * Referenced by: '<S7>/Gain4'
   */
  0.507,

  /* Expression: 55.0
   * Referenced by: '<S7>/Constant1'
   */
  55.0,

  /* Expression: 6.84
   * Referenced by: '<S4>/Gain'
   */
  6.84,

  /* Expression: 416
   * Referenced by: '<S2>/Saturation6'
   */
  416.0,

  /* Expression: 0
   * Referenced by: '<S2>/Saturation6'
   */
  0.0,

  /* Expression: 1/38.5
   * Referenced by: '<S4>/Gain1'
   */
  0.025974025974025976,

  /* Expression: 0
   * Referenced by: '<S3>/Integrator'
   */
  0.0,

  /* Expression: 4
   * Referenced by: '<S2>/Saturation3'
   */
  4.0,

  /* Expression: 0
   * Referenced by: '<S2>/Saturation3'
   */
  0.0,

  /* Expression: 16
   * Referenced by: '<S2>/Saturation5'
   */
  16.0,

  /* Expression: 0
   * Referenced by: '<S2>/Saturation5'
   */
  0.0,

  /* Expression: 1/20
   * Referenced by: '<S5>/Gain'
   */
  0.05,

  /* Expression: 200
   * Referenced by: '<Root>/X1_Step'
   */
  200.0,

  /* Expression: 5
   * Referenced by: '<Root>/X1_Step'
   */
  5.0,

  /* Expression: 35
   * Referenced by: '<Root>/X1_Step'
   */
  35.0,

  /* Expression: 1/20
   * Referenced by: '<S7>/Gain'
   */
  0.05,

  /* Expression: 16
   * Referenced by: '<S7>/Saturation2'
   */
  16.0,

  /* Expression: 0
   * Referenced by: '<S7>/Saturation2'
   */
  0.0,

  /* Expression: 1/4
   * Referenced by: '<S7>/Gain1'
   */
  0.25,

  /* Expression: 1/1.2
   * Referenced by: '<S3>/Gain'
   */
  0.83333333333333337
};
