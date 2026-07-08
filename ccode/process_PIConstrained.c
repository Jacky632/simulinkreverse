/*
 * process_PIConstrained.c
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
#include "rtwtypes.h"
#include "process_PIConstrained_private.h"

/* Block signals (default storage) */
B_process_PIConstrained_T process_PIConstrained_B;

/* Continuous states */
X_process_PIConstrained_T process_PIConstrained_X;

/* Disabled State Vector */
XDis_process_PIConstrained_T process_PIConstrained_XDis;

/* External outputs (root outports fed by signals with default storage) */
ExtY_process_PIConstrained_T process_PIConstrained_Y;

/* Real-time model */
static RT_MODEL_process_PIConstraine_T process_PIConstrained_M_;
RT_MODEL_process_PIConstraine_T *const process_PIConstrained_M =
  &process_PIConstrained_M_;

/*
 * This function updates continuous states using the ODE3 fixed-step
 * solver algorithm
 */
static void rt_ertODEUpdateContinuousStates(RTWSolverInfo *si )
{
  /* Solver Matrices */
  static const real_T rt_ODE3_A[3] = {
    1.0/2.0, 3.0/4.0, 1.0
  };

  static const real_T rt_ODE3_B[3][3] = {
    { 1.0/2.0, 0.0, 0.0 },

    { 0.0, 3.0/4.0, 0.0 },

    { 2.0/9.0, 1.0/3.0, 4.0/9.0 }
  };

  time_T t = rtsiGetT(si);
  time_T tnew = rtsiGetSolverStopTime(si);
  time_T h = rtsiGetStepSize(si);
  real_T *x = rtsiGetContStates(si);
  ODE3_IntgData *id = (ODE3_IntgData *)rtsiGetSolverData(si);
  real_T *y = id->y;
  real_T *f0 = id->f[0];
  real_T *f1 = id->f[1];
  real_T *f2 = id->f[2];
  real_T hB[3];
  int_T i;
  int_T nXc = 5;
  rtsiSetSimTimeStep(si,MINOR_TIME_STEP);

  /* Save the state values at time t in y, we'll use x as ynew. */
  (void) memcpy(y, x,
                (uint_T)nXc*sizeof(real_T));

  /* Assumes that rtsiSetT and ModelOutputs are up-to-date */
  /* f0 = f(t,y) */
  rtsiSetdX(si, f0);
  process_PIConstrained_derivatives();

  /* f(:,2) = feval(odefile, t + hA(1), y + f*hB(:,1), args(:)(*)); */
  hB[0] = h * rt_ODE3_B[0][0];
  for (i = 0; i < nXc; i++) {
    x[i] = y[i] + (f0[i]*hB[0]);
  }

  rtsiSetT(si, t + h*rt_ODE3_A[0]);
  rtsiSetdX(si, f1);
  process_PIConstrained_step();
  process_PIConstrained_derivatives();

  /* f(:,3) = feval(odefile, t + hA(2), y + f*hB(:,2), args(:)(*)); */
  for (i = 0; i <= 1; i++) {
    hB[i] = h * rt_ODE3_B[1][i];
  }

  for (i = 0; i < nXc; i++) {
    x[i] = y[i] + (f0[i]*hB[0] + f1[i]*hB[1]);
  }

  rtsiSetT(si, t + h*rt_ODE3_A[1]);
  rtsiSetdX(si, f2);
  process_PIConstrained_step();
  process_PIConstrained_derivatives();

  /* tnew = t + hA(3);
     ynew = y + f*hB(:,3); */
  for (i = 0; i <= 2; i++) {
    hB[i] = h * rt_ODE3_B[2][i];
  }

  for (i = 0; i < nXc; i++) {
    x[i] = y[i] + (f0[i]*hB[0] + f1[i]*hB[1] + f2[i]*hB[2]);
  }

  rtsiSetT(si, tnew);
  rtsiSetSimTimeStep(si,MAJOR_TIME_STEP);
}

/* Model step function */
void process_PIConstrained_step(void)
{
  real_T u0;
  real_T u1;
  real_T u2;
  if (rtmIsMajorTimeStep(process_PIConstrained_M)) {
    /* set solver stop time */
    if (!(process_PIConstrained_M->Timing.clockTick0+1)) {
      rtsiSetSolverStopTime(&process_PIConstrained_M->solverInfo,
                            ((process_PIConstrained_M->Timing.clockTickH0 + 1) *
        process_PIConstrained_M->Timing.stepSize0 * 4294967296.0));
    } else {
      rtsiSetSolverStopTime(&process_PIConstrained_M->solverInfo,
                            ((process_PIConstrained_M->Timing.clockTick0 + 1) *
        process_PIConstrained_M->Timing.stepSize0 +
        process_PIConstrained_M->Timing.clockTickH0 *
        process_PIConstrained_M->Timing.stepSize0 * 4294967296.0));
    }
  }                                    /* end MajorTimeStep */

  /* Update absolute time of base rate at minor time step */
  if (rtmIsMinorTimeStep(process_PIConstrained_M)) {
    process_PIConstrained_M->Timing.t[0] = rtsiGetT
      (&process_PIConstrained_M->solverInfo);
  }

  /* Integrator: '<S5>/L2Int' */
  process_PIConstrained_B.L2Int = process_PIConstrained_X.L2Int_CSTATE;

  /* Saturate: '<S2>/Saturation' */
  u0 = process_PIConstrained_B.L2Int;
  u1 = process_PIConstrained_P.Saturation_LowerSat;
  u2 = process_PIConstrained_P.Saturation_UpperSat;
  if (u0 > u2) {
    /* Saturate: '<S2>/Saturation' */
    process_PIConstrained_B.Saturation = u2;
  } else if (u0 < u1) {
    /* Saturate: '<S2>/Saturation' */
    process_PIConstrained_B.Saturation = u1;
  } else {
    /* Saturate: '<S2>/Saturation' */
    process_PIConstrained_B.Saturation = u0;
  }

  /* End of Saturate: '<S2>/Saturation' */

  /* Outport: '<Root>/L2' */
  process_PIConstrained_Y.L2 = process_PIConstrained_B.Saturation;

  /* Step: '<Root>/F1_Step' */
  u0 = process_PIConstrained_M->Timing.t[0];
  if (u0 < process_PIConstrained_P.F1_Step_Time) {
    /* Step: '<Root>/F1_Step' */
    process_PIConstrained_B.F1_Step = process_PIConstrained_P.F1_Step_Y0;
  } else {
    /* Step: '<Root>/F1_Step' */
    process_PIConstrained_B.F1_Step = process_PIConstrained_P.F1_Step_YFinal;
  }

  /* End of Step: '<Root>/F1_Step' */

  /* Sum: '<S6>/Sum1' incorporates:
   *  Constant: '<Root>/F3'
   */
  process_PIConstrained_B.Sum1 = process_PIConstrained_B.F1_Step +
    process_PIConstrained_P.F3_Value;

  /* Gain: '<S6>/Gain1' */
  process_PIConstrained_B.Gain1 = process_PIConstrained_P.Gain1_Gain *
    process_PIConstrained_B.Sum1;
  if (rtmIsMajorTimeStep(process_PIConstrained_M)) {
    /* Saturate: '<S2>/Saturation2' incorporates:
     *  Constant: '<Root>/P100'
     */
    u0 = process_PIConstrained_P.P100_Value;
    u1 = process_PIConstrained_P.Saturation2_LowerSat;
    u2 = process_PIConstrained_P.Saturation2_UpperSat;
    if (u0 > u2) {
      /* Saturate: '<S2>/Saturation2' */
      process_PIConstrained_B.Saturation2 = u2;
    } else if (u0 < u1) {
      /* Saturate: '<S2>/Saturation2' */
      process_PIConstrained_B.Saturation2 = u1;
    } else {
      /* Saturate: '<S2>/Saturation2' */
      process_PIConstrained_B.Saturation2 = u0;
    }

    /* End of Saturate: '<S2>/Saturation2' */

    /* Gain: '<S6>/Gain' */
    process_PIConstrained_B.Gain = process_PIConstrained_P.Gain_Gain *
      process_PIConstrained_B.Saturation2;

    /* Sum: '<S6>/Sum' incorporates:
     *  Constant: '<S6>/Constant1'
     */
    process_PIConstrained_B.Sum = process_PIConstrained_P.Constant1_Value +
      process_PIConstrained_B.Gain;
  }

  /* Integrator: '<S7>/X2Int' */
  process_PIConstrained_B.X2Int = process_PIConstrained_X.X2Int_CSTATE;

  /* Gain: '<S7>/Gain3' */
  process_PIConstrained_B.Gain3 = process_PIConstrained_P.Gain3_Gain *
    process_PIConstrained_B.X2Int;

  /* Integrator: '<S7>/P2Int' */
  process_PIConstrained_B.P2Int = process_PIConstrained_X.P2Int_CSTATE;

  /* Saturate: '<S7>/Saturation1' */
  u0 = process_PIConstrained_B.P2Int;
  u1 = process_PIConstrained_P.Saturation1_LowerSat;
  u2 = process_PIConstrained_P.Saturation1_UpperSat;
  if (u0 > u2) {
    /* Saturate: '<S7>/Saturation1' */
    process_PIConstrained_B.Saturation1 = u2;
  } else if (u0 < u1) {
    /* Saturate: '<S7>/Saturation1' */
    process_PIConstrained_B.Saturation1 = u1;
  } else {
    /* Saturate: '<S7>/Saturation1' */
    process_PIConstrained_B.Saturation1 = u0;
  }

  /* End of Saturate: '<S7>/Saturation1' */

  /* Gain: '<S7>/Gain2' */
  process_PIConstrained_B.Gain2 = process_PIConstrained_P.Gain2_Gain *
    process_PIConstrained_B.Saturation1;

  /* Sum: '<S7>/Sum2' incorporates:
   *  Constant: '<S7>/Constant'
   */
  process_PIConstrained_B.Sum2 = (process_PIConstrained_B.Gain3 +
    process_PIConstrained_P.Constant_Value) + process_PIConstrained_B.Gain2;

  /* Sum: '<S6>/Sum2' */
  process_PIConstrained_B.Sum2_o = process_PIConstrained_B.Sum -
    process_PIConstrained_B.Sum2;

  /* Product: '<S6>/Product' */
  process_PIConstrained_B.Product = process_PIConstrained_B.Gain1 *
    process_PIConstrained_B.Sum2_o;

  /* Sum: '<S7>/Sum5' incorporates:
   *  Constant: '<Root>/T1'
   */
  process_PIConstrained_B.Sum5 = process_PIConstrained_B.Sum2 -
    process_PIConstrained_P.T1_Value;

  /* Product: '<S7>/Product2' */
  process_PIConstrained_B.Product2 = process_PIConstrained_B.Sum5 *
    process_PIConstrained_B.F1_Step;

  /* Gain: '<S7>/Gain5' */
  process_PIConstrained_B.Gain5 = process_PIConstrained_P.Gain5_Gain *
    process_PIConstrained_B.Product2;

  /* Sum: '<S7>/Sum4' */
  process_PIConstrained_B.Sum4 = process_PIConstrained_B.Product -
    process_PIConstrained_B.Gain5;

  /* Gain: '<S7>/Gain6' */
  process_PIConstrained_B.Gain6 = process_PIConstrained_P.Gain6_Gain *
    process_PIConstrained_B.Sum4;

  /* Saturate: '<S7>/Saturation' */
  u0 = process_PIConstrained_B.Gain6;
  u1 = process_PIConstrained_P.Saturation_LowerSat_k;
  u2 = process_PIConstrained_P.Saturation_UpperSat_p;
  if (u0 > u2) {
    /* Saturate: '<S7>/Saturation' */
    process_PIConstrained_B.Saturation_p = u2;
  } else if (u0 < u1) {
    /* Saturate: '<S7>/Saturation' */
    process_PIConstrained_B.Saturation_p = u1;
  } else {
    /* Saturate: '<S7>/Saturation' */
    process_PIConstrained_B.Saturation_p = u0;
  }

  /* End of Saturate: '<S7>/Saturation' */

  /* Saturate: '<S2>/Saturation4' */
  u0 = process_PIConstrained_B.Saturation_p;
  u1 = process_PIConstrained_P.Saturation4_LowerSat;
  u2 = process_PIConstrained_P.Saturation4_UpperSat;
  if (u0 > u2) {
    /* Saturate: '<S2>/Saturation4' */
    process_PIConstrained_B.Saturation4 = u2;
  } else if (u0 < u1) {
    /* Saturate: '<S2>/Saturation4' */
    process_PIConstrained_B.Saturation4 = u1;
  } else {
    /* Saturate: '<S2>/Saturation4' */
    process_PIConstrained_B.Saturation4 = u0;
  }

  /* End of Saturate: '<S2>/Saturation4' */
  if (rtmIsMajorTimeStep(process_PIConstrained_M)) {
  }

  /* Integrator: '<Root>/FeedbackInt' */
  process_PIConstrained_B.FeedbackInt =
    process_PIConstrained_X.FeedbackInt_CSTATE;

  /* Step: '<Root>/L2 Set Point' */
  u0 = process_PIConstrained_M->Timing.t[0];
  if (u0 < process_PIConstrained_P.L2SetPoint_Time) {
    /* Step: '<Root>/L2 Set Point' */
    process_PIConstrained_B.L2SetPoint = process_PIConstrained_P.L2SetPoint_Y0;
  } else {
    /* Step: '<Root>/L2 Set Point' */
    process_PIConstrained_B.L2SetPoint =
      process_PIConstrained_P.L2SetPoint_YFinal;
  }

  /* End of Step: '<Root>/L2 Set Point' */

  /* Sum: '<Root>/Sum' */
  process_PIConstrained_B.Sum_k = process_PIConstrained_B.L2SetPoint
    - process_PIConstrained_B.Saturation;

  /* Gain: '<S1>/Slider Gain' */
  process_PIConstrained_B.SliderGain =
    process_PIConstrained_P.L2ProportionalGain_gain *
    process_PIConstrained_B.Sum_k;

  /* Sum: '<Root>/Sum2' */
  process_PIConstrained_B.Sum2_oi = process_PIConstrained_B.SliderGain +
    process_PIConstrained_B.FeedbackInt;

  /* Sum: '<Root>/Sum1' incorporates:
   *  Constant: '<Root>/F2'
   */
  process_PIConstrained_B.Sum1_g = process_PIConstrained_P.F2_Value +
    process_PIConstrained_B.Sum2_oi;

  /* Gain: '<Root>/Ti ' */
  process_PIConstrained_B.Ti = process_PIConstrained_P.Ti_Gain *
    process_PIConstrained_B.SliderGain;

  /* Gain: '<S7>/Gain4' */
  process_PIConstrained_B.Gain4 = process_PIConstrained_P.Gain4_Gain *
    process_PIConstrained_B.Saturation1;

  /* Sum: '<S7>/Sum3' incorporates:
   *  Constant: '<S7>/Constant1'
   */
  process_PIConstrained_B.Sum3 = process_PIConstrained_B.Gain4 +
    process_PIConstrained_P.Constant1_Value_i;

  /* Sum: '<S4>/Sum' incorporates:
   *  Constant: '<Root>/T200'
   */
  process_PIConstrained_B.Sum_d = process_PIConstrained_B.Sum3 -
    process_PIConstrained_P.T200_Value;

  /* Gain: '<S4>/Gain' */
  process_PIConstrained_B.Gain_c = process_PIConstrained_P.Gain_Gain_h *
    process_PIConstrained_B.Sum_d;
  if (rtmIsMajorTimeStep(process_PIConstrained_M)) {
    /* Saturate: '<S2>/Saturation6' incorporates:
     *  Constant: '<Root>/F200'
     */
    u0 = process_PIConstrained_P.F200_Value;
    u1 = process_PIConstrained_P.Saturation6_LowerSat;
    u2 = process_PIConstrained_P.Saturation6_UpperSat;
    if (u0 > u2) {
      /* Saturate: '<S2>/Saturation6' */
      process_PIConstrained_B.Saturation6 = u2;
    } else if (u0 < u1) {
      /* Saturate: '<S2>/Saturation6' */
      process_PIConstrained_B.Saturation6 = u1;
    } else {
      /* Saturate: '<S2>/Saturation6' */
      process_PIConstrained_B.Saturation6 = u0;
    }

    /* End of Saturate: '<S2>/Saturation6' */

    /* Product: '<S4>/Product' incorporates:
     *  Constant: '<S4>/Constant'
     *  Constant: '<S4>/Constant1'
     */
    process_PIConstrained_B.Product_k = process_PIConstrained_P.Constant_Value_c
      / process_PIConstrained_P.Constant1_Value_h /
      process_PIConstrained_B.Saturation6;

    /* Sum: '<S4>/Sum1' incorporates:
     *  Constant: '<S4>/Constant2'
     */
    process_PIConstrained_B.Sum1_h = process_PIConstrained_P.Constant2_Value +
      process_PIConstrained_B.Product_k;
  }

  /* Product: '<S4>/Product1' */
  process_PIConstrained_B.Q200 = process_PIConstrained_B.Gain_c /
    process_PIConstrained_B.Sum1_h;

  /* Gain: '<S4>/Gain1' */
  process_PIConstrained_B.Gain1_a = process_PIConstrained_P.Gain1_Gain_l *
    process_PIConstrained_B.Q200;

  /* Integrator: '<S3>/Integrator' */
  process_PIConstrained_B.Integrator = process_PIConstrained_X.Integrator_CSTATE;

  /* Saturate: '<S2>/Saturation3' */
  u0 = process_PIConstrained_B.Integrator;
  u1 = process_PIConstrained_P.Saturation3_LowerSat;
  u2 = process_PIConstrained_P.Saturation3_UpperSat;
  if (u0 > u2) {
    /* Saturate: '<S2>/Saturation3' */
    process_PIConstrained_B.Saturation3 = u2;
  } else if (u0 < u1) {
    /* Saturate: '<S2>/Saturation3' */
    process_PIConstrained_B.Saturation3 = u1;
  } else {
    /* Saturate: '<S2>/Saturation3' */
    process_PIConstrained_B.Saturation3 = u0;
  }

  /* End of Saturate: '<S2>/Saturation3' */

  /* Saturate: '<S2>/Saturation5' */
  u0 = process_PIConstrained_B.Gain1_a;
  u1 = process_PIConstrained_P.Saturation5_LowerSat;
  u2 = process_PIConstrained_P.Saturation5_UpperSat;
  if (u0 > u2) {
    /* Saturate: '<S2>/Saturation5' */
    process_PIConstrained_B.Saturation5 = u2;
  } else if (u0 < u1) {
    /* Saturate: '<S2>/Saturation5' */
    process_PIConstrained_B.Saturation5 = u1;
  } else {
    /* Saturate: '<S2>/Saturation5' */
    process_PIConstrained_B.Saturation5 = u0;
  }

  /* End of Saturate: '<S2>/Saturation5' */

  /* Sum: '<S5>/Sum' */
  process_PIConstrained_B.Sum_m = (process_PIConstrained_B.F1_Step -
    process_PIConstrained_B.Saturation3) - process_PIConstrained_B.Saturation4;

  /* Gain: '<S5>/Gain' */
  process_PIConstrained_B.Gain_g = process_PIConstrained_P.Gain_Gain_k *
    process_PIConstrained_B.Sum_m;

  /* Step: '<Root>/X1_Step' */
  u0 = process_PIConstrained_M->Timing.t[0];
  if (u0 < process_PIConstrained_P.X1_Step_Time) {
    /* Step: '<Root>/X1_Step' */
    process_PIConstrained_B.X1_Step = process_PIConstrained_P.X1_Step_Y0;
  } else {
    /* Step: '<Root>/X1_Step' */
    process_PIConstrained_B.X1_Step = process_PIConstrained_P.X1_Step_YFinal;
  }

  /* End of Step: '<Root>/X1_Step' */

  /* Product: '<S7>/Product' */
  process_PIConstrained_B.Product_c = process_PIConstrained_B.F1_Step *
    process_PIConstrained_B.X1_Step;

  /* Product: '<S7>/Product1' */
  process_PIConstrained_B.Product1 = process_PIConstrained_B.Saturation3 *
    process_PIConstrained_B.X2Int;

  /* Sum: '<S7>/Sum' */
  process_PIConstrained_B.Sum_i = process_PIConstrained_B.Product_c -
    process_PIConstrained_B.Product1;

  /* Gain: '<S7>/Gain' */
  process_PIConstrained_B.Gain_a = process_PIConstrained_P.Gain_Gain_n *
    process_PIConstrained_B.Sum_i;

  /* Saturate: '<S7>/Saturation2' */
  u0 = process_PIConstrained_B.Saturation_p;
  u1 = process_PIConstrained_P.Saturation2_LowerSat_a;
  u2 = process_PIConstrained_P.Saturation2_UpperSat_l;
  if (u0 > u2) {
    /* Saturate: '<S7>/Saturation2' */
    process_PIConstrained_B.Saturation2_e = u2;
  } else if (u0 < u1) {
    /* Saturate: '<S7>/Saturation2' */
    process_PIConstrained_B.Saturation2_e = u1;
  } else {
    /* Saturate: '<S7>/Saturation2' */
    process_PIConstrained_B.Saturation2_e = u0;
  }

  /* End of Saturate: '<S7>/Saturation2' */

  /* Sum: '<S7>/Sum1' */
  process_PIConstrained_B.Sum1_e = process_PIConstrained_B.Saturation2_e -
    process_PIConstrained_B.Saturation5;

  /* Gain: '<S7>/Gain1' */
  process_PIConstrained_B.Gain1_f = process_PIConstrained_P.Gain1_Gain_m *
    process_PIConstrained_B.Sum1_e;

  /* Sum: '<S3>/Sum' */
  process_PIConstrained_B.Sum_iw = process_PIConstrained_B.Sum1_g -
    process_PIConstrained_B.Integrator;

  /* Gain: '<S3>/Gain' */
  process_PIConstrained_B.Gain_b = process_PIConstrained_P.Gain_Gain_hu *
    process_PIConstrained_B.Sum_iw;
  if (rtmIsMajorTimeStep(process_PIConstrained_M)) {
    /* Matfile logging */
    rt_UpdateTXYLogVars(process_PIConstrained_M->rtwLogInfo,
                        (process_PIConstrained_M->Timing.t));
  }                                    /* end MajorTimeStep */

  if (rtmIsMajorTimeStep(process_PIConstrained_M)) {
    /* signal main to stop simulation */
    {                                  /* Sample time: [0.0s, 0.0s] */
      if ((rtmGetTFinal(process_PIConstrained_M)!=-1) &&
          !((rtmGetTFinal(process_PIConstrained_M)-
             (((process_PIConstrained_M->Timing.clockTick1+
                process_PIConstrained_M->Timing.clockTickH1* 4294967296.0)) *
              18.0)) > (((process_PIConstrained_M->Timing.clockTick1+
                          process_PIConstrained_M->Timing.clockTickH1*
                          4294967296.0)) * 18.0) * (DBL_EPSILON))) {
        rtmSetErrorStatus(process_PIConstrained_M, "Simulation finished");
      }
    }

    rt_ertODEUpdateContinuousStates(&process_PIConstrained_M->solverInfo);

    /* Update absolute time for base rate */
    /* The "clockTick0" counts the number of times the code of this task has
     * been executed. The absolute time is the multiplication of "clockTick0"
     * and "Timing.stepSize0". Size of "clockTick0" ensures timer will not
     * overflow during the application lifespan selected.
     * Timer of this task consists of two 32 bit unsigned integers.
     * The two integers represent the low bits Timing.clockTick0 and the high bits
     * Timing.clockTickH0. When the low bit overflows to 0, the high bits increment.
     */
    if (!(++process_PIConstrained_M->Timing.clockTick0)) {
      ++process_PIConstrained_M->Timing.clockTickH0;
    }

    process_PIConstrained_M->Timing.t[0] = rtsiGetSolverStopTime
      (&process_PIConstrained_M->solverInfo);

    {
      /* Update absolute timer for sample time: [18.0s, 0.0s] */
      /* The "clockTick1" counts the number of times the code of this task has
       * been executed. The resolution of this integer timer is 18.0, which is the step size
       * of the task. Size of "clockTick1" ensures timer will not overflow during the
       * application lifespan selected.
       * Timer of this task consists of two 32 bit unsigned integers.
       * The two integers represent the low bits Timing.clockTick1 and the high bits
       * Timing.clockTickH1. When the low bit overflows to 0, the high bits increment.
       */
      process_PIConstrained_M->Timing.clockTick1++;
      if (!process_PIConstrained_M->Timing.clockTick1) {
        process_PIConstrained_M->Timing.clockTickH1++;
      }
    }
  }                                    /* end MajorTimeStep */
}

/* Derivatives for root system: '<Root>' */
void process_PIConstrained_derivatives(void)
{
  XDot_process_PIConstrained_T *_rtXdot;
  _rtXdot = ((XDot_process_PIConstrained_T *) process_PIConstrained_M->derivs);

  /* Derivatives for Integrator: '<S5>/L2Int' */
  _rtXdot->L2Int_CSTATE = process_PIConstrained_B.Gain_g;

  /* Derivatives for Integrator: '<S7>/X2Int' */
  _rtXdot->X2Int_CSTATE = process_PIConstrained_B.Gain_a;

  /* Derivatives for Integrator: '<S7>/P2Int' */
  _rtXdot->P2Int_CSTATE = process_PIConstrained_B.Gain1_f;

  /* Derivatives for Integrator: '<Root>/FeedbackInt' */
  _rtXdot->FeedbackInt_CSTATE = process_PIConstrained_B.Ti;

  /* Derivatives for Integrator: '<S3>/Integrator' */
  _rtXdot->Integrator_CSTATE = process_PIConstrained_B.Gain_b;
}

/* Model initialize function */
void process_PIConstrained_initialize(void)
{
  /* Registration code */

  /* initialize real-time model */
  (void) memset((void *)process_PIConstrained_M, 0,
                sizeof(RT_MODEL_process_PIConstraine_T));

  {
    /* Setup solver object */
    rtsiSetSimTimeStepPtr(&process_PIConstrained_M->solverInfo,
                          &process_PIConstrained_M->Timing.simTimeStep);
    rtsiSetTPtr(&process_PIConstrained_M->solverInfo, &rtmGetTPtr
                (process_PIConstrained_M));
    rtsiSetStepSizePtr(&process_PIConstrained_M->solverInfo,
                       &process_PIConstrained_M->Timing.stepSize0);
    rtsiSetdXPtr(&process_PIConstrained_M->solverInfo,
                 &process_PIConstrained_M->derivs);
    rtsiSetContStatesPtr(&process_PIConstrained_M->solverInfo, (real_T **)
                         &process_PIConstrained_M->contStates);
    rtsiSetNumContStatesPtr(&process_PIConstrained_M->solverInfo,
      &process_PIConstrained_M->Sizes.numContStates);
    rtsiSetNumPeriodicContStatesPtr(&process_PIConstrained_M->solverInfo,
      &process_PIConstrained_M->Sizes.numPeriodicContStates);
    rtsiSetPeriodicContStateIndicesPtr(&process_PIConstrained_M->solverInfo,
      &process_PIConstrained_M->periodicContStateIndices);
    rtsiSetPeriodicContStateRangesPtr(&process_PIConstrained_M->solverInfo,
      &process_PIConstrained_M->periodicContStateRanges);
    rtsiSetContStateDisabledPtr(&process_PIConstrained_M->solverInfo, (boolean_T**)
      &process_PIConstrained_M->contStateDisabled);
    rtsiSetErrorStatusPtr(&process_PIConstrained_M->solverInfo,
                          (&rtmGetErrorStatus(process_PIConstrained_M)));
    rtsiSetRTModelPtr(&process_PIConstrained_M->solverInfo,
                      process_PIConstrained_M);
  }

  rtsiSetSimTimeStep(&process_PIConstrained_M->solverInfo, MAJOR_TIME_STEP);
  rtsiSetIsMinorTimeStepWithModeChange(&process_PIConstrained_M->solverInfo,
    false);
  rtsiSetIsContModeFrozen(&process_PIConstrained_M->solverInfo, false);
  process_PIConstrained_M->intgData.y = process_PIConstrained_M->odeY;
  process_PIConstrained_M->intgData.f[0] = process_PIConstrained_M->odeF[0];
  process_PIConstrained_M->intgData.f[1] = process_PIConstrained_M->odeF[1];
  process_PIConstrained_M->intgData.f[2] = process_PIConstrained_M->odeF[2];
  process_PIConstrained_M->contStates = ((X_process_PIConstrained_T *)
    &process_PIConstrained_X);
  process_PIConstrained_M->contStateDisabled = ((XDis_process_PIConstrained_T *)
    &process_PIConstrained_XDis);
  process_PIConstrained_M->Timing.tStart = (0.0);
  rtsiSetSolverData(&process_PIConstrained_M->solverInfo, (void *)
                    &process_PIConstrained_M->intgData);
  rtsiSetSolverName(&process_PIConstrained_M->solverInfo,"ode3");
  rtmSetTPtr(process_PIConstrained_M, &process_PIConstrained_M->Timing.tArray[0]);
  rtmSetTFinal(process_PIConstrained_M, 900.0);
  process_PIConstrained_M->Timing.stepSize0 = 18.0;

  /* Setup for data logging */
  {
    static RTWLogInfo rt_DataLoggingInfo;
    rt_DataLoggingInfo.loggingInterval = (NULL);
    process_PIConstrained_M->rtwLogInfo = &rt_DataLoggingInfo;
  }

  /* Setup for data logging */
  {
    rtliSetLogXSignalInfo(process_PIConstrained_M->rtwLogInfo, (NULL));
    rtliSetLogXSignalPtrs(process_PIConstrained_M->rtwLogInfo, (NULL));
    rtliSetLogT(process_PIConstrained_M->rtwLogInfo, "tout");
    rtliSetLogX(process_PIConstrained_M->rtwLogInfo, "");
    rtliSetLogXFinal(process_PIConstrained_M->rtwLogInfo, "");
    rtliSetLogVarNameModifier(process_PIConstrained_M->rtwLogInfo, "rt_");
    rtliSetLogFormat(process_PIConstrained_M->rtwLogInfo, 4);
    rtliSetLogMaxRows(process_PIConstrained_M->rtwLogInfo, 0);
    rtliSetLogDecimation(process_PIConstrained_M->rtwLogInfo, 1);
    rtliSetLogY(process_PIConstrained_M->rtwLogInfo, "");
    rtliSetLogYSignalInfo(process_PIConstrained_M->rtwLogInfo, (NULL));
    rtliSetLogYSignalPtrs(process_PIConstrained_M->rtwLogInfo, (NULL));
  }

  /* block I/O */
  (void) memset(((void *) &process_PIConstrained_B), 0,
                sizeof(B_process_PIConstrained_T));

  /* states (continuous) */
  {
    (void) memset((void *)&process_PIConstrained_X, 0,
                  sizeof(X_process_PIConstrained_T));
  }

  /* disabled states */
  {
    (void) memset((void *)&process_PIConstrained_XDis, 0,
                  sizeof(XDis_process_PIConstrained_T));
  }

  /* external outputs */
  process_PIConstrained_Y.L2 = 0.0;

  /* Matfile logging */
  rt_StartDataLoggingWithStartTime(process_PIConstrained_M->rtwLogInfo, 0.0,
    rtmGetTFinal(process_PIConstrained_M),
    process_PIConstrained_M->Timing.stepSize0, (&rtmGetErrorStatus
    (process_PIConstrained_M)));

  /* InitializeConditions for Integrator: '<S5>/L2Int' */
  process_PIConstrained_X.L2Int_CSTATE = process_PIConstrained_P.L2Int_IC;

  /* InitializeConditions for Integrator: '<S7>/X2Int' */
  process_PIConstrained_X.X2Int_CSTATE = process_PIConstrained_P.X2Int_IC;

  /* InitializeConditions for Integrator: '<S7>/P2Int' */
  process_PIConstrained_X.P2Int_CSTATE = process_PIConstrained_P.P2Int_IC;

  /* InitializeConditions for Integrator: '<Root>/FeedbackInt' */
  process_PIConstrained_X.FeedbackInt_CSTATE =
    process_PIConstrained_P.FeedbackInt_IC;

  /* InitializeConditions for Integrator: '<S3>/Integrator' */
  process_PIConstrained_X.Integrator_CSTATE =
    process_PIConstrained_P.Integrator_IC;
}

/* Model terminate function */
void process_PIConstrained_terminate(void)
{
  /* (no terminate code required) */
}
