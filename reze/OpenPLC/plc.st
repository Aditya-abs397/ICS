PROGRAM HVAC_Control
  VAR
    Occupancy AT %IX0.3 : BOOL;
    HVAC_Enable AT %QX0.3 : BOOL;
    Cooling AT %QX0.0 : BOOL;
    Heating AT %QX0.1 : BOOL;
    Tank_Level AT %MW0 : INT;
  END_VAR

  IF Occupancy THEN
    HVAC_Enable := TRUE;
    Tank_Level := Tank_Level + 1;
  ELSE
    HVAC_Enable := FALSE;
  END_IF;

  IF Tank_Level > 100 THEN
    Tank_Level := 0;
  END_IF;

  Cooling := HVAC_Enable;

END_PROGRAM

CONFIGURATION Config0
  RESOURCE Res0 ON PLC
    TASK TaskMain(INTERVAL := T#100ms, PRIORITY := 0);
    PROGRAM Inst0 WITH TaskMain : HVAC_Control;
  END_RESOURCE
END_CONFIGURATION
