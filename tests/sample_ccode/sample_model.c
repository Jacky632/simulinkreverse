#include "sample_model.h"

B_sample_model_T sample_model_B;
DW_sample_model_T sample_model_DW;
ExtU_sample_model_T sample_model_U;
ExtY_sample_model_T sample_model_Y;
P_sample_model_T sample_model_P = {
  2.0,
  5.0,
  0.0
};

void sample_model_initialize(void)
{
  /* InitializeConditions for UnitDelay: '<Root>/Unit Delay' */
  sample_model_DW.UnitDelay_DSTATE = sample_model_P.UnitDelay_InitialCondition;
}

void sample_model_step(void)
{
  /* Gain: '<Root>/Gain' */
  sample_model_B.gainOut = sample_model_P.K * sample_model_U.u;

  /* Sum: '<Root>/Sum' */
  sample_model_B.sumOut = sample_model_B.gainOut + sample_model_U.v;

  /* Product: '<Root>/Product' */
  sample_model_B.productOut = sample_model_B.sumOut * sample_model_U.v;

  /* Constant: '<Root>/Constant' */
  sample_model_B.constOut = sample_model_P.C_Value;

  /* UnitDelay: '<Root>/Unit Delay' */
  sample_model_B.delayOut = sample_model_DW.UnitDelay_DSTATE;

  /* Outport: '<Root>/y' */
  sample_model_Y.y = sample_model_B.productOut;

  /* Update for UnitDelay: '<Root>/Unit Delay' */
  sample_model_DW.UnitDelay_DSTATE = sample_model_U.u;
}

void sample_model_terminate(void)
{
}
