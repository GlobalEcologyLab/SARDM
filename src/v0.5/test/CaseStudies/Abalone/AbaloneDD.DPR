library AbaloneDD;
// This function implements a combined Ricker and Allee DD model
// Initial stage matrix should have an eigenvalue = Rmax
// Density dependence basis must be "Selected Stages"
// In Stages, Basis for DD must be "No" for some stages and "Yes" for some stages
// Allee parameter must be specified under the "User-defined" tab (not "Density
//      dependence" tab) of the Populations dialog

{$R+,I+,Q+}

uses
  Dll_Intf;

const
  UserParameterCount = 1;

//---------------------------------------------------------------------------
// This procedure is called once when the simulation starts, before
// ComputeDensityDependence is called.
procedure InitializeSimulation(
      Replications  : Cardinal;   //number of replications for simulation
      Duration      : Cardinal;   //number of timsteps for simulation
      Populations   : Cardinal;   //number of populations
      Stages        : Cardinal;   //number of stages
  var UserErrorCode : Integer); stdcall;
begin
//popcount:=populations;
end; //InitializeSimulation


procedure FinalizeSimulation; stdcall;
begin
//close(fout);
//close(fsum);
end; //FinalizeSimulation



//---------------------------------------------------------------------------
procedure ComputeDensityDependence(
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
        AverageMates      : Double;  //females per male (if polygynous) or
                                     //males per female (if polyandrous)
                                     //=+1 (if monogamous)
                                     //=-1 (if "unlimited")

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

  //This DLL should only change the following parameters
        TMatrix           : TDoubleMatrixPtr; //Transition matrix for this population
        //Usage: TMatrix^[ToStage]^[FromStage] where ToStage and FromStage are
        //integers 1..stages.  The values of the array are single reals; they
        //incorporate "Relative survival" and "Relative fecundity" parameters

      //Error handling:
  var userDDErrorCode     : Integer;      //code for error in this function (see below)
  var userDDErrorMsg      : TCharArray);  // message string about the error (see below)
      //code=0 : no error
      //code=1 : display the message at the end of simulation
      //code>1 : terminate simulation immediately and display the message
      //code<0 : display the message immediately, continue simulation, set code=0,
      //         and delete the message (thus, 1 message displayed per function call)

  stdcall; // THIS LINE MUST REMAIN


//---------------------------------------------------------------------------

const
  exp_biggest = 60.0;
  pow_biggest = 2.6e30;
var
  i,j : Integer;
  PopSize, lMult, Allee, fMult : double;
  AllBasis : boolean;
  // ss, fn:string;
begin
  if (ThisReplication=0) then exit;

  if (ThisReplication=1) and (timestep=1) and (popIndex=1) then
    begin

    if DDbasis<>SelectedStages then
      begin
      userDDErrorCode := 2;
      userDDErrorMsg  := 'This function must be based on Selected Stages';
      end;

    AllBasis:=true;
    for j:=1 to stages do if (not BasisForDD^[j]) then AllBasis:=false;
    if AllBasis then
      begin
      userDDErrorCode := 2;
      userDDErrorMsg  := 'Error: all stages are included in the DD basis';
      end;

    userDDErrorCode := -2;
    userDDErrorMsg  := 'Note: this function assumes that eigenvalue of the stage matrix=Rmax';

    end;

  // RICKER
  if Rmax<=1 then
      begin
      userDDErrorCode := 2;
      userDDErrorMsg  := 'Rmax must be > 1';
      end;

  PopSize:=0;

  for j:=1 to stages do if BasisforDD^[j] then PopSize := PopSize + Nstage^[j];

  if carryingCapacity <= 0 then
    lMult := 0
  else {see equation for "Scramble" in section 8.4 of the User Manual}
   BEGIN
   lMult := (-ln(Rmax) / CarryingCapacity) * PopSize;

   if Abs(lMult)<exp_biggest
       then lMult := exp(lMult)
       else if lMult>0 then lMult := pow_biggest
                       else lMult := 1/pow_biggest;
   lMult := Rmax * lMult;
   END;

   for i := 1 to Stages do
      for j := 1 to Stages do
          TMatrix^[i]^[j] := lMult * TMatrix^[i]^[j];
   // end - Ricker

   // Allee
     PopSize:=0;
     Allee := userParams[1];
     for j:=1 to stages do PopSize := PopSize + Reproductive^[j] * Nstage^[j];

     if (PopSize<Allee) and (Allee>0) then
     begin
     fMult:=PopSize/Allee;

     for i := 1 to Stages do
        for j := 1 to Stages do
            if ConstraintsMatrix^[i]^[j]<0.5 then
                 TMatrix^[i]^[j] := fMult * TMatrix^[i]^[j];
     end;



end; //ComputeDensityDependence

const
  UserParameterNames: array[1..UserParameterCount] of PChar = (
    'Allee');
  UserParameterMinimums: array[1..UserParameterCount] of Double = (
    0);
  UserParameterMaximums: array[1..UserParameterCount] of Double = (
    9999999);
  UserParameterDefaults: array[1..UserParameterCount] of Double = (
    1);
  UserParameterDecimals: array[1..UserParameterCount] of Cardinal = (
    0);


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


exports
  ComputeDensityDependence,
  GetUserParametersInfo,
  InitializeSimulation,
  FinalizeSimulation;


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
