/*
 * Code generation for model "sample_model".
 */
#ifndef sample_model_h_
#define sample_model_h_

typedef double real_T;

typedef struct {
  real_T u;                            /* '<Root>/u' */
  real_T v;                            /* '<Root>/v' */
} ExtU_sample_model_T;

typedef struct {
  real_T gainOut;                      /* '<Root>/Gain' */
  real_T sumOut;                       /* '<Root>/Sum' */
  real_T productOut;                   /* '<Root>/Product' */
  real_T constOut;                     /* '<Root>/Constant' */
  real_T delayOut;                     /* '<Root>/Unit Delay' */
} B_sample_model_T;

typedef struct {
  real_T UnitDelay_DSTATE;             /* '<Root>/Unit Delay' */
} DW_sample_model_T;

typedef struct {
  real_T y;                            /* '<Root>/y' */
} ExtY_sample_model_T;

struct P_sample_model_T_ {
  real_T K;                            /* Expression: 2
                                        * Referenced by: '<Root>/Gain'
                                        */
  real_T C_Value;                      /* Expression: 5
                                        * Referenced by: '<Root>/Constant'
                                        */
  real_T UnitDelay_InitialCondition;   /* Expression: 0
                                        * Referenced by: '<Root>/Unit Delay'
                                        */
};

typedef struct P_sample_model_T_ P_sample_model_T;

extern B_sample_model_T sample_model_B;
extern DW_sample_model_T sample_model_DW;
extern ExtU_sample_model_T sample_model_U;
extern ExtY_sample_model_T sample_model_Y;
extern P_sample_model_T sample_model_P;

extern void sample_model_initialize(void);
extern void sample_model_step(void);
extern void sample_model_terminate(void);

#endif
