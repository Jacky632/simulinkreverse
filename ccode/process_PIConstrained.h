/*
 * process_PIConstrained.h
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

#ifndef process_PIConstrained_h_
#define process_PIConstrained_h_
#ifndef process_PIConstrained_COMMON_INCLUDES_
#define process_PIConstrained_COMMON_INCLUDES_
#include "rtwtypes.h"
#include "rtw_continuous.h"
#include "rtw_solver.h"
#include "rt_logging.h"
#include "rt_nonfinite.h"
#include "math.h"
#endif                              /* process_PIConstrained_COMMON_INCLUDES_ */

#include "process_PIConstrained_types.h"
#include <float.h>
#include <string.h>
#include <stddef.h>

/* Macros for accessing real-time model data structure */
#ifndef rtmGetContStateDisabled
#define rtmGetContStateDisabled(rtm)   ((rtm)->contStateDisabled)
#endif

#ifndef rtmSetContStateDisabled
#define rtmSetContStateDisabled(rtm, val) ((rtm)->contStateDisabled = (val))
#endif

#ifndef rtmGetContStates
#define rtmGetContStates(rtm)          ((rtm)->contStates)
#endif

#ifndef rtmSetContStates
#define rtmSetContStates(rtm, val)     ((rtm)->contStates = (val))
#endif

#ifndef rtmGetContTimeOutputInconsistentWithStateAtMajorStepFlag
#define rtmGetContTimeOutputInconsistentWithStateAtMajorStepFlag(rtm) ((rtm)->CTOutputIncnstWithState)
#endif

#ifndef rtmSetContTimeOutputInconsistentWithStateAtMajorStepFlag
#define rtmSetContTimeOutputInconsistentWithStateAtMajorStepFlag(rtm, val) ((rtm)->CTOutputIncnstWithState = (val))
#endif

#ifndef rtmGetDerivCacheNeedsReset
#define rtmGetDerivCacheNeedsReset(rtm) ((rtm)->derivCacheNeedsReset)
#endif

#ifndef rtmSetDerivCacheNeedsReset
#define rtmSetDerivCacheNeedsReset(rtm, val) ((rtm)->derivCacheNeedsReset = (val))
#endif

#ifndef rtmGetFinalTime
#define rtmGetFinalTime(rtm)           ((rtm)->Timing.tFinal)
#endif

#ifndef rtmGetIntgData
#define rtmGetIntgData(rtm)            ((rtm)->intgData)
#endif

#ifndef rtmSetIntgData
#define rtmSetIntgData(rtm, val)       ((rtm)->intgData = (val))
#endif

#ifndef rtmGetOdeF
#define rtmGetOdeF(rtm)                ((rtm)->odeF)
#endif

#ifndef rtmSetOdeF
#define rtmSetOdeF(rtm, val)           ((rtm)->odeF = (val))
#endif

#ifndef rtmGetOdeY
#define rtmGetOdeY(rtm)                ((rtm)->odeY)
#endif

#ifndef rtmSetOdeY
#define rtmSetOdeY(rtm, val)           ((rtm)->odeY = (val))
#endif

#ifndef rtmGetPeriodicContStateIndices
#define rtmGetPeriodicContStateIndices(rtm) ((rtm)->periodicContStateIndices)
#endif

#ifndef rtmSetPeriodicContStateIndices
#define rtmSetPeriodicContStateIndices(rtm, val) ((rtm)->periodicContStateIndices = (val))
#endif

#ifndef rtmGetPeriodicContStateRanges
#define rtmGetPeriodicContStateRanges(rtm) ((rtm)->periodicContStateRanges)
#endif

#ifndef rtmSetPeriodicContStateRanges
#define rtmSetPeriodicContStateRanges(rtm, val) ((rtm)->periodicContStateRanges = (val))
#endif

#ifndef rtmGetRTWLogInfo
#define rtmGetRTWLogInfo(rtm)          ((rtm)->rtwLogInfo)
#endif

#ifndef rtmGetZCCacheNeedsReset
#define rtmGetZCCacheNeedsReset(rtm)   ((rtm)->zCCacheNeedsReset)
#endif

#ifndef rtmSetZCCacheNeedsReset
#define rtmSetZCCacheNeedsReset(rtm, val) ((rtm)->zCCacheNeedsReset = (val))
#endif

#ifndef rtmGetdX
#define rtmGetdX(rtm)                  ((rtm)->derivs)
#endif

#ifndef rtmSetdX
#define rtmSetdX(rtm, val)             ((rtm)->derivs = (val))
#endif

#ifndef rtmGetErrorStatus
#define rtmGetErrorStatus(rtm)         ((rtm)->errorStatus)
#endif

#ifndef rtmSetErrorStatus
#define rtmSetErrorStatus(rtm, val)    ((rtm)->errorStatus = (val))
#endif

#ifndef rtmGetStopRequested
#define rtmGetStopRequested(rtm)       ((rtm)->Timing.stopRequestedFlag)
#endif

#ifndef rtmSetStopRequested
#define rtmSetStopRequested(rtm, val)  ((rtm)->Timing.stopRequestedFlag = (val))
#endif

#ifndef rtmGetStopRequestedPtr
#define rtmGetStopRequestedPtr(rtm)    (&((rtm)->Timing.stopRequestedFlag))
#endif

#ifndef rtmGetT
#define rtmGetT(rtm)                   (rtmGetTPtr((rtm))[0])
#endif

#ifndef rtmGetTFinal
#define rtmGetTFinal(rtm)              ((rtm)->Timing.tFinal)
#endif

#ifndef rtmGetTPtr
#define rtmGetTPtr(rtm)                ((rtm)->Timing.t)
#endif

#ifndef rtmGetTStart
#define rtmGetTStart(rtm)              ((rtm)->Timing.tStart)
#endif

/* Block signals (default storage) */
typedef struct {
  real_T L2Int;                        /* '<S5>/L2Int' */
  real_T Saturation;                   /* '<S2>/Saturation' */
  real_T F1_Step;                      /* '<Root>/F1_Step' */
  real_T Sum1;                         /* '<S6>/Sum1' */
  real_T Gain1;                        /* '<S6>/Gain1' */
  real_T Saturation2;                  /* '<S2>/Saturation2' */
  real_T Gain;                         /* '<S6>/Gain' */
  real_T Sum;                          /* '<S6>/Sum' */
  real_T X2Int;                        /* '<S7>/X2Int' */
  real_T Gain3;                        /* '<S7>/Gain3' */
  real_T P2Int;                        /* '<S7>/P2Int' */
  real_T Saturation1;                  /* '<S7>/Saturation1' */
  real_T Gain2;                        /* '<S7>/Gain2' */
  real_T Sum2;                         /* '<S7>/Sum2' */
  real_T Sum2_o;                       /* '<S6>/Sum2' */
  real_T Product;                      /* '<S6>/Product' */
  real_T Sum5;                         /* '<S7>/Sum5' */
  real_T Product2;                     /* '<S7>/Product2' */
  real_T Gain5;                        /* '<S7>/Gain5' */
  real_T Sum4;                         /* '<S7>/Sum4' */
  real_T Gain6;                        /* '<S7>/Gain6' */
  real_T Saturation_p;                 /* '<S7>/Saturation' */
  real_T Saturation4;                  /* '<S2>/Saturation4' */
  real_T FeedbackInt;                  /* '<Root>/FeedbackInt' */
  real_T L2SetPoint;                   /* '<Root>/L2 Set Point' */
  real_T Sum_k;                        /* '<Root>/Sum' */
  real_T SliderGain;                   /* '<S1>/Slider Gain' */
  real_T Sum2_oi;                      /* '<Root>/Sum2' */
  real_T Sum1_g;                       /* '<Root>/Sum1' */
  real_T Ti;                           /* '<Root>/Ti ' */
  real_T Gain4;                        /* '<S7>/Gain4' */
  real_T Sum3;                         /* '<S7>/Sum3' */
  real_T Sum_d;                        /* '<S4>/Sum' */
  real_T Gain_c;                       /* '<S4>/Gain' */
  real_T Saturation6;                  /* '<S2>/Saturation6' */
  real_T Product_k;                    /* '<S4>/Product' */
  real_T Sum1_h;                       /* '<S4>/Sum1' */
  real_T Q200;                         /* '<S4>/Product1' */
  real_T Gain1_a;                      /* '<S4>/Gain1' */
  real_T Integrator;                   /* '<S3>/Integrator' */
  real_T Saturation3;                  /* '<S2>/Saturation3' */
  real_T Saturation5;                  /* '<S2>/Saturation5' */
  real_T Sum_m;                        /* '<S5>/Sum' */
  real_T Gain_g;                       /* '<S5>/Gain' */
  real_T X1_Step;                      /* '<Root>/X1_Step' */
  real_T Product_c;                    /* '<S7>/Product' */
  real_T Product1;                     /* '<S7>/Product1' */
  real_T Sum_i;                        /* '<S7>/Sum' */
  real_T Gain_a;                       /* '<S7>/Gain' */
  real_T Saturation2_e;                /* '<S7>/Saturation2' */
  real_T Sum1_e;                       /* '<S7>/Sum1' */
  real_T Gain1_f;                      /* '<S7>/Gain1' */
  real_T Sum_iw;                       /* '<S3>/Sum' */
  real_T Gain_b;                       /* '<S3>/Gain' */
} B_process_PIConstrained_T;

/* Continuous states (default storage) */
typedef struct {
  real_T L2Int_CSTATE;                 /* '<S5>/L2Int' */
  real_T X2Int_CSTATE;                 /* '<S7>/X2Int' */
  real_T P2Int_CSTATE;                 /* '<S7>/P2Int' */
  real_T FeedbackInt_CSTATE;           /* '<Root>/FeedbackInt' */
  real_T Integrator_CSTATE;            /* '<S3>/Integrator' */
} X_process_PIConstrained_T;

/* State derivatives (default storage) */
typedef struct {
  real_T L2Int_CSTATE;                 /* '<S5>/L2Int' */
  real_T X2Int_CSTATE;                 /* '<S7>/X2Int' */
  real_T P2Int_CSTATE;                 /* '<S7>/P2Int' */
  real_T FeedbackInt_CSTATE;           /* '<Root>/FeedbackInt' */
  real_T Integrator_CSTATE;            /* '<S3>/Integrator' */
} XDot_process_PIConstrained_T;

/* State disabled  */
typedef struct {
  boolean_T L2Int_CSTATE;              /* '<S5>/L2Int' */
  boolean_T X2Int_CSTATE;              /* '<S7>/X2Int' */
  boolean_T P2Int_CSTATE;              /* '<S7>/P2Int' */
  boolean_T FeedbackInt_CSTATE;        /* '<Root>/FeedbackInt' */
  boolean_T Integrator_CSTATE;         /* '<S3>/Integrator' */
} XDis_process_PIConstrained_T;

#ifndef ODE3_INTG
#define ODE3_INTG

/* ODE3 Integration Data */
typedef struct {
  real_T *y;                           /* output */
  real_T *f[3];                        /* derivatives */
} ODE3_IntgData;

#endif

/* External outputs (root outports fed by signals with default storage) */
typedef struct {
  real_T L2;                           /* '<Root>/L2' */
} ExtY_process_PIConstrained_T;

/* Parameters (default storage) */
struct P_process_PIConstrained_T_ {
  real_T L2ProportionalGain_gain;     /* Mask Parameter: L2ProportionalGain_gain
                                       * Referenced by: '<S1>/Slider Gain'
                                       */
  real_T L2Int_IC;                     /* Expression: 1
                                        * Referenced by: '<S5>/L2Int'
                                        */
  real_T Saturation_UpperSat;          /* Expression: 2
                                        * Referenced by: '<S2>/Saturation'
                                        */
  real_T Saturation_LowerSat;          /* Expression: 0
                                        * Referenced by: '<S2>/Saturation'
                                        */
  real_T F1_Step_Time;                 /* Expression: 200
                                        * Referenced by: '<Root>/F1_Step'
                                        */
  real_T F1_Step_Y0;                   /* Expression: 10
                                        * Referenced by: '<Root>/F1_Step'
                                        */
  real_T F1_Step_YFinal;               /* Expression: 10
                                        * Referenced by: '<Root>/F1_Step'
                                        */
  real_T F3_Value;                     /* Expression: 50
                                        * Referenced by: '<Root>/F3'
                                        */
  real_T Gain1_Gain;                   /* Expression: 0.16
                                        * Referenced by: '<S6>/Gain1'
                                        */
  real_T Constant1_Value;              /* Expression: 90
                                        * Referenced by: '<S6>/Constant1'
                                        */
  real_T P100_Value;                   /* Expression: 194.7
                                        * Referenced by: '<Root>/P100'
                                        */
  real_T Saturation2_UpperSat;         /* Expression: 400
                                        * Referenced by: '<S2>/Saturation2'
                                        */
  real_T Saturation2_LowerSat;         /* Expression: 0
                                        * Referenced by: '<S2>/Saturation2'
                                        */
  real_T Gain_Gain;                    /* Expression: 0.1538
                                        * Referenced by: '<S6>/Gain'
                                        */
  real_T X2Int_IC;                     /* Expression: 25
                                        * Referenced by: '<S7>/X2Int'
                                        */
  real_T Gain3_Gain;                   /* Expression: 0.3126
                                        * Referenced by: '<S7>/Gain3'
                                        */
  real_T Constant_Value;               /* Expression: 48.43
                                        * Referenced by: '<S7>/Constant'
                                        */
  real_T P2Int_IC;                     /* Expression: 50.5
                                        * Referenced by: '<S7>/P2Int'
                                        */
  real_T Saturation1_UpperSat;         /* Expression: 100
                                        * Referenced by: '<S7>/Saturation1'
                                        */
  real_T Saturation1_LowerSat;         /* Expression: 0
                                        * Referenced by: '<S7>/Saturation1'
                                        */
  real_T Gain2_Gain;                   /* Expression: 0.5616
                                        * Referenced by: '<S7>/Gain2'
                                        */
  real_T T1_Value;                     /* Expression: 40
                                        * Referenced by: '<Root>/T1'
                                        */
  real_T Gain5_Gain;                   /* Expression: 0.07
                                        * Referenced by: '<S7>/Gain5'
                                        */
  real_T Gain6_Gain;                   /* Expression: 1/38.5
                                        * Referenced by: '<S7>/Gain6'
                                        */
  real_T Saturation_UpperSat_p;        /* Expression: 16
                                        * Referenced by: '<S7>/Saturation'
                                        */
  real_T Saturation_LowerSat_k;        /* Expression: 0
                                        * Referenced by: '<S7>/Saturation'
                                        */
  real_T Saturation4_UpperSat;         /* Expression: 16
                                        * Referenced by: '<S2>/Saturation4'
                                        */
  real_T Saturation4_LowerSat;         /* Expression: 0
                                        * Referenced by: '<S2>/Saturation4'
                                        */
  real_T F2_Value;                     /* Expression: 2
                                        * Referenced by: '<Root>/F2'
                                        */
  real_T F200_Value;                   /* Expression: 208
                                        * Referenced by: '<Root>/F200'
                                        */
  real_T FeedbackInt_IC;               /* Expression: 0
                                        * Referenced by: '<Root>/FeedbackInt'
                                        */
  real_T L2SetPoint_Time;              /* Expression: 200
                                        * Referenced by: '<Root>/L2 Set Point'
                                        */
  real_T L2SetPoint_Y0;                /* Expression: 1
                                        * Referenced by: '<Root>/L2 Set Point'
                                        */
  real_T L2SetPoint_YFinal;            /* Expression: 1
                                        * Referenced by: '<Root>/L2 Set Point'
                                        */
  real_T T200_Value;                   /* Expression: 25
                                        * Referenced by: '<Root>/T200'
                                        */
  real_T Ti_Gain;                      /* Expression: 1/18.93
                                        * Referenced by: '<Root>/Ti '
                                        */
  real_T Constant_Value_c;             /* Expression: 6.84
                                        * Referenced by: '<S4>/Constant'
                                        */
  real_T Constant1_Value_h;            /* Expression: 2*0.07
                                        * Referenced by: '<S4>/Constant1'
                                        */
  real_T Constant2_Value;              /* Expression: 1
                                        * Referenced by: '<S4>/Constant2'
                                        */
  real_T Gain4_Gain;                   /* Expression: 0.507
                                        * Referenced by: '<S7>/Gain4'
                                        */
  real_T Constant1_Value_i;            /* Expression: 55.0
                                        * Referenced by: '<S7>/Constant1'
                                        */
  real_T Gain_Gain_h;                  /* Expression: 6.84
                                        * Referenced by: '<S4>/Gain'
                                        */
  real_T Saturation6_UpperSat;         /* Expression: 416
                                        * Referenced by: '<S2>/Saturation6'
                                        */
  real_T Saturation6_LowerSat;         /* Expression: 0
                                        * Referenced by: '<S2>/Saturation6'
                                        */
  real_T Gain1_Gain_l;                 /* Expression: 1/38.5
                                        * Referenced by: '<S4>/Gain1'
                                        */
  real_T Integrator_IC;                /* Expression: 0
                                        * Referenced by: '<S3>/Integrator'
                                        */
  real_T Saturation3_UpperSat;         /* Expression: 4
                                        * Referenced by: '<S2>/Saturation3'
                                        */
  real_T Saturation3_LowerSat;         /* Expression: 0
                                        * Referenced by: '<S2>/Saturation3'
                                        */
  real_T Saturation5_UpperSat;         /* Expression: 16
                                        * Referenced by: '<S2>/Saturation5'
                                        */
  real_T Saturation5_LowerSat;         /* Expression: 0
                                        * Referenced by: '<S2>/Saturation5'
                                        */
  real_T Gain_Gain_k;                  /* Expression: 1/20
                                        * Referenced by: '<S5>/Gain'
                                        */
  real_T X1_Step_Time;                 /* Expression: 200
                                        * Referenced by: '<Root>/X1_Step'
                                        */
  real_T X1_Step_Y0;                   /* Expression: 5
                                        * Referenced by: '<Root>/X1_Step'
                                        */
  real_T X1_Step_YFinal;               /* Expression: 35
                                        * Referenced by: '<Root>/X1_Step'
                                        */
  real_T Gain_Gain_n;                  /* Expression: 1/20
                                        * Referenced by: '<S7>/Gain'
                                        */
  real_T Saturation2_UpperSat_l;       /* Expression: 16
                                        * Referenced by: '<S7>/Saturation2'
                                        */
  real_T Saturation2_LowerSat_a;       /* Expression: 0
                                        * Referenced by: '<S7>/Saturation2'
                                        */
  real_T Gain1_Gain_m;                 /* Expression: 1/4
                                        * Referenced by: '<S7>/Gain1'
                                        */
  real_T Gain_Gain_hu;                 /* Expression: 1/1.2
                                        * Referenced by: '<S3>/Gain'
                                        */
};

/* Real-time Model Data Structure */
struct tag_RTM_process_PIConstrained_T {
  const char_T *errorStatus;
  RTWLogInfo *rtwLogInfo;
  RTWSolverInfo solverInfo;
  X_process_PIConstrained_T *contStates;
  int_T *periodicContStateIndices;
  real_T *periodicContStateRanges;
  real_T *derivs;
  XDis_process_PIConstrained_T *contStateDisabled;
  boolean_T zCCacheNeedsReset;
  boolean_T derivCacheNeedsReset;
  boolean_T CTOutputIncnstWithState;
  real_T odeY[5];
  real_T odeF[3][5];
  ODE3_IntgData intgData;

  /*
   * Sizes:
   * The following substructure contains sizes information
   * for many of the model attributes such as inputs, outputs,
   * dwork, sample times, etc.
   */
  struct {
    int_T numContStates;
    int_T numPeriodicContStates;
    int_T numSampTimes;
  } Sizes;

  /*
   * Timing:
   * The following substructure contains information regarding
   * the timing information for the model.
   */
  struct {
    uint32_T clockTick0;
    uint32_T clockTickH0;
    time_T stepSize0;
    uint32_T clockTick1;
    uint32_T clockTickH1;
    time_T tStart;
    time_T tFinal;
    SimTimeStep simTimeStep;
    boolean_T stopRequestedFlag;
    time_T *t;
    time_T tArray[2];
  } Timing;
};

/* Block parameters (default storage) */
extern P_process_PIConstrained_T process_PIConstrained_P;

/* Block signals (default storage) */
extern B_process_PIConstrained_T process_PIConstrained_B;

/* Continuous states (default storage) */
extern X_process_PIConstrained_T process_PIConstrained_X;

/* Disabled states (default storage) */
extern XDis_process_PIConstrained_T process_PIConstrained_XDis;

/* External outputs (root outports fed by signals with default storage) */
extern ExtY_process_PIConstrained_T process_PIConstrained_Y;

/* Model entry point functions */
extern void process_PIConstrained_initialize(void);
extern void process_PIConstrained_step(void);
extern void process_PIConstrained_terminate(void);

/* Real-time Model object */
extern RT_MODEL_process_PIConstraine_T *const process_PIConstrained_M;

/*-
 * These blocks were eliminated from the model due to optimizations:
 *
 * Block '<S4>/Constant3' : Unused code path elimination
 * Block '<S4>/Product2' : Unused code path elimination
 * Block '<S4>/Sum2' : Unused code path elimination
 * Block '<S2>/Saturation1' : Unused code path elimination
 * Block '<S6>/Gain2' : Unused code path elimination
 */

/*-
 * The generated code includes comments that allow you to trace directly
 * back to the appropriate location in the model.  The basic format
 * is <system>/block_name, where system is the system number (uniquely
 * assigned by Simulink) and block_name is the name of the block.
 *
 * Use the MATLAB hilite_system command to trace the generated code back
 * to the model.  For example,
 *
 * hilite_system('<S3>')    - opens system 3
 * hilite_system('<S3>/Kp') - opens and selects block Kp which resides in S3
 *
 * Here is the system hierarchy for this model
 *
 * '<Root>' : 'process_PIConstrained'
 * '<S1>'   : 'process_PIConstrained/L2 Proportional Gain'
 * '<S2>'   : 'process_PIConstrained/Whole Process'
 * '<S3>'   : 'process_PIConstrained/delay'
 * '<S4>'   : 'process_PIConstrained/Whole Process/Condenser'
 * '<S5>'   : 'process_PIConstrained/Whole Process/Separator'
 * '<S6>'   : 'process_PIConstrained/Whole Process/Steamjacket'
 * '<S7>'   : 'process_PIConstrained/Whole Process/evaporator'
 */
#endif                                 /* process_PIConstrained_h_ */
