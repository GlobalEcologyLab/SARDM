library NLNTurtle;
// This DLL implements a density dependence function for the 
// Northern Long-necked Turtle (Chelodina rugosa).
// DD affects hatchling survival (Surv0), thus fecundities.
// Fecundities in the stage matrix must be for Surv0 = 1.0.
// The MaxS0 and DDb parameters must be entered under the "User-defined"  
// tab in the Population dialog for the first population.  
// The user-defined parameters for populations after the first one are ignored.
// The Rmax parameter under the "Density dependence" tab is ignored.
//
// Fecundities in the stage matrix are mutiplied with Surv0, calculated as
//       Surv0 = MaxS0 * exp( DDb * (N/K) )
// with default parameter values:
//       Surv0 = 0.9385 * exp(-3.88 * (N/K) )
//
// In addition, user must specify in the MP file
// * In Density Dependence dialog:
//           "Density dependence (and carrying capacity) is based on the abundance of"
// * In Stages dialog:
//           Basis for DD (Yes or No for each stage)
// * In Populations dialog:
//           K
//      NOTE: K is not necessarily the equilibrium abundance; the equilibrium
//      pop size is determined by the function parameters and the stage matrix.
//      K also depends on which stages are Basis for DD

{$R+,I+,Q+}

uses
  DLL_Intf, Math;

const
  UserParameterCount = 2;

const
  UserParameterNames: array[1..UserParameterCount] of PANSIChar = (
    'MaxS0','DDb');
  UserParameterMinimums: array[1..UserParameterCount] of Double = (
    0,-10);
  UserParameterMaximums: array[1..UserParameterCount] of Double = (
    1,0);
  UserParameterDefaults: array[1..UserParameterCount] of Double = (
    0.9385,-3.88);
  UserParameterDecimals: array[1..UserParameterCount] of Cardinal = (
    5,3);

//---------------------------------------------------------------------------
procedure GetUserParametersInfo(
  var names   : TPCharArrayPtr;
  var minimums: TDoubleArrayPtr;
  var maximums: TDoubleArrayPtr;
  var defaults: TDoubleArrayPtr;
  var decimals: TCardinalArrayPtr;
  var count   : Integer); stdcall;
begin
  names    := @UserParameterNames;
  minimums := @UserParameterMinimums;
  maximums := @UserParameterMaximums;
  defaults := @UserParameterDefaults;
  decimals := @UserParameterDecimals;
  count    := High(UserParameterNames);
end; //GetUserParametersInfo


  var
   popcount : Integer;
   MaxS0 , DDb : real;

procedure InitializeSimulation(
      Replications  : Cardinal;   //number of replications for simulation
      Duration      : Cardinal;   //number of timsteps for simulation
      Populations   : Cardinal;   //number of populations
      Stages        : Cardinal;   //number of stages
  var UserErrorCode : Integer); stdcall;
begin
popcount:=populations;
end; //InitializeSimulation

procedure FinalizeSimulation; stdcall;
begin
end; //FinalizeSimulation


//---------------------------------------------------------------------------
procedure ComputeDensityDependence(
//This DLL should NOT change the values of the following parameters:
      ThisReplication   : Cardinal; //current replication of the simulation
      Replications      : Cardinal; //number of replications in this simulation
      Timestep          : Cardinal; //current time step of the simulation
      Duration          : Cardinal; //duration (number of time steps) in this simulation
      PopIndex          : Cardinal; //index for this population
      Stages            : Cardinal; //number of stages in the model

      SexStructure      : SexStructureType; //which sex(es) modeled; see manual

      // The following 3 parameters should be used ONLY if SexStructure=TwoSexes
      FemaleStages      : Cardinal;         //number of female stages
      MatingSystem      : MatingSystemType; //see manual
      AverageMates      : Double;           //females per male (if polygynous) or
                                          //males per female (if polyandrous)
                                          //=1 (if monogamous)

      // stage arrays (vectors of stage-specific parameters)
      AvgWeight         : TSingleArrayPtr;  //average weight of individuals in stage
      Exclude           : TBooleanArrayPtr; //whether stage is excluded from total N
      BasisForDD        : TBooleanArrayPtr; //whether stage is used as a basis for
                                          //dens dep (used only if DDbasis=selectedstages)
      Reproductive      : TDoubleArrayPtr;  //proportion of reproductive individuals

      //DD parameters
      DDaffects         : DDactionType;     //which vital rates affected by DD
      DDbasis           : DDBasisType;      //which abundance is DD based on
      Rmax              : Double;           //maximum growth rate for this population
      CarryingCapacity  : Double;           //K for this population

      //Abundance parameters
      N                 : Integer;          //total abundance of this population
      Nstage            : TLongIntArrayPtr; //abundance in each stage
      //Note: N = sum of Nstage (even if exclude=True for some stages)

      ConstraintsMatrix : TDoubleMatrixPtr; //see manual

      UserParams        : TDoubleArrayPtr;  //user-defined parameters

      //This DLL can change the following parameters
      TMatrix           : TDoubleMatrixPtr; //Transition matrix for this population
      //Incorporates "Relative survival" and "Relative fecundity" parameters

      //Error handling:
  var userDDErrorCode     : Integer;      //code for error in this function (see below)
  var userDDErrorMsg      : TCharArray);  // message string about the error (see below)
      //code=0 : no error
      //code=1 : display the message at the end of simulation
      //code>1 : terminate simulation immediately and display the message
      //code<0 : display the message immediately, continue simulation, set code=0,
      //         and delete the message (thus, 1 message displayed per function call)

  stdcall; // THIS LINE MUST REMAIN


var
  Surv0: real;
  PopSize, TotalFec : real;
  i, j : integer;
  
// ****************************************************************************

begin //Procedure ComputeDensityDependence

if (ThisReplication<=1) and (PopIndex<=1) and (TimeStep<=1) then
   begin
   MaxS0 := userParams[1];
   DDb     := userParams[2];
   end;


   PopSize:=0;
   case DDBasis of
       AllStages     : PopSize := N;
       SelectedStages: for j:=1 to stages do if BasisForDD^[j] then
                           PopSize := PopSize + Nstage^[j];
       FecWeighted   : for j:=1 to stages do
                           begin
                           TotalFec:=0; // fecundity of stage j
                           for i:=1 to stages do TotalFec := TotalFec +
                                    TMatrix^[i]^[j]*(1-ConstraintsMatrix[i,j]);
                           PopSize := PopSize + TotalFec * Nstage^[j]
                           end;
       end; // case DDBasis


if (CarryingCapacity<=0) 
   then Surv0 := 0                        // KTS 9/22/2013: added "MAX" to avoid underflow error
   else  Surv0 := Max(MaxS0 * exp( DDb * (PopSize / CarryingCapacity) ),1e-8);

  for i := 1 to Stages do
      for j := 1 to Stages do
          TMatrix^[i]^[j] := (1-ConstraintsMatrix[i,j]) * Surv0 * TMatrix^[i]^[j]
 		+ConstraintsMatrix^[i]^[j] * Tmatrix^[i]^[j];

end; // Procedure ComputeDensityDependence



exports
  InitializeSimulation,
  FinalizeSimulation,
  ComputeDensityDependence,
  GetUserParametersInfo;

// the following code lets the compiler verify that the function definitions
// match the type definitions
var
  ComputeDensityDependenceFunctionCheck : ComputeDensityDependenceFunctionType;
  GetUserParametersInfoFunctionCheck    : GetUserParametersInfoFunctionType;

begin
  ComputeDensityDependenceFunctionCheck := ComputeDensityDependence;
  if Assigned(ComputeDensityDependenceFunctionCheck) then
    ;

  GetUserParametersInfoFunctionCheck := GetUserParametersInfo;
  if Assigned(GetUserParametersInfoFunctionCheck) then
    ;
end.
