# Firefly Interpreter Documentation

## Overview

The Firefly Interpreter is a powerful scripting engine that allows you to create dynamic automation programs using your GUI panels. You can reference panel values, create custom variables, control actuators, and manage program execution flow.

## Basic Syntax

### Variables and Assignments
```javascript
// Reference panel values (panels act as variables)
PumpStatus = WaterPump;
if TempSensor > 30 HeatingElement = 0;
```

### Operators
```javascript
// Arithmetic
Result = 10 + 5;        // Addition
Result = 10 - 3;        // Subtraction  
Result = 4 * 6;         // Multiplication
Result = 20 / 4;        // Division

// Comparison
Temperature > 25        // Greater than
Humidity < 60          // Less than
Level == 100           // Equal to (also can use 'is')
Pressure is 14.7       // Alternative equality

// Logical
Pump & Valve           // AND operation
Day | Night            // OR operation
!EmergencyStop         // NOT operation
```

## Panel Integration

### Using Panels as Variables

Your GUI panels automatically become variables that can be read and modified:

```javascript
// Read panel values
CurrentTemp = TemperatureSensor;
WaterLevel = LevelGauge;

// Control actuators through panels
HeatingElement = 1;     // Turn on heating
WaterPump = 0;          // Turn off pump
FanSpeed = 75;          // Set fan to 75%

// Use timer panels
Timer1 = 300;           // Set timer to 5 minutes (300 seconds)
if Timer1 == 0 PumpProgram = 0;  // Stop program when timer expires
```

### Output Panel Control

```javascript
// Control digital outputs
Output1 = 1;            // Turn on output 1
Output2 = 0;            // Turn off output 2

// Control PWM outputs  
PWMOutput1 = 128;       // 50% duty cycle (0-255 range)
LEDStrip = 200;         // Bright LED setting
```

## Custom Variables

Create your own global variables with the web app to use in program logic:

```javascript
// Use in calculations
TempDiff = CurrentTemp - LastTemp;
LastTemp = CurrentTemp;

// State tracking
if WaterLow PumpState = 1;
```

## Program Control

### One-Shot Programs

Programs that run once and shut themselves off:

```javascript
// Pump priming program named PrimingProgram
if StartPriming WaterPump = 1;
if StartPriming pause 5;
if StartPriming WaterPump = 0;
if StartPriming PrimingProgram = 0;

// Toggle on Infrared Remote program named IR_toggle
if IR == 13 D3 = !D3;
if IR == 13 IR_toggle = 0;
```

### Program Interaction

Programs can control other programs:

```javascript
// Master control program
if SystemStart HeatingProgram = 1;
if SystemStart PumpProgram = 1;
if SystemStart MonitoringProgram = 1;

if SystemStop HeatingProgram = 0;
if SystemStop PumpProgram = 0;
if SystemStop MonitoringProgram = 0;
if SystemStop MasterControl = 0;

// Conditional program starting
if Temperature < 20 HeatingProgram = 1;
if Temperature > 30 HeatingProgram = 0;
```

## Practical Examples

### 1. Temperature Control System

```javascript
// HeatingProgram
if Temperature < SetPoint - 2 Heater = 1;
if Temperature < SetPoint - 2 HeaterStatus = 1;

if Temperature > SetPoint + 1 Heater = 0;
if Temperature > SetPoint + 1 HeaterStatus = 0;

// Display current status
HeaterDisplay = HeaterStatus;
```

### 2. Water Level Management

```javascript
// WaterLevelProgram  
if WaterLevel < 20 FillPump = 1;
if WaterLevel < 20 LowWaterAlarm = 1;

if WaterLevel > 80 FillPump = 0;
if WaterLevel > 80 LowWaterAlarm = 0;

// Emergency overflow protection
if WaterLevel > 95 FillPump = 0;
if WaterLevel > 95 DrainValve = 1;
if WaterLevel > 95 OverflowAlarm = 1;
```

### 3. Timer-Based Operations
   Programs can turn on Timer panels:
```javascript
// CycleProgram
if StartCycle Timer1 = 1;
if StartCycle Pump = 1;
if StartCycle StartCycle = 0;

if Timer1 == 0 & Pump == 1 Pump = 0;
if Timer1 == 0 & Pump == 1 Timer2 = 30;

if Timer2 == 0 CycleProgram = 0;
```

### 4. Multi-Stage Process Control

```javascript
// ProcessControl
if Stage == 1 Valve1 = 1;
if Stage == 1 & FlowSensor > 50 Stage = 2;

if Stage == 2 Valve1 = 0;
if Stage == 2 Heater = 1;
if Stage == 2 & Temperature > TargetTemp Stage = 3;

if Stage == 3 Heater = 0;
if Stage == 3 Mixer = 1;
if Stage == 3 Timer1 = 120;
if Stage == 3 & Timer1 == 0 Stage = 4;

if Stage == 4 Mixer = 0;
if Stage == 4 ProcessComplete = 1;
if Stage == 4 ProcessControl = 0;
```

### 5. Safety Monitoring

```javascript
// SafetyMonitor
if Temperature > MaxTemp | Pressure > MaxPressure EmergencyStop = 1;
if Temperature > MaxTemp | Pressure > MaxPressure AllPrograms = 0;

if EmergencyStop Heater = 0;
if EmergencyStop Pump = 0;
if EmergencyStop AllValves = 0;
if EmergencyStop AlarmBuzzer = 1;

// Reset capability
if ResetButton & !EmergencyStop AlarmBuzzer = 0;
if ResetButton & !EmergencyStop SafetyMonitor = 0;
```

### 6. Data Logging and Monitoring

```javascript
// DataLogger
LogCounter = LogCounter + 1;

if LogCounter >= 60 LoggedTemp = Temperature;
if LogCounter >= 60 LoggedPressure = Pressure;
if LogCounter >= 60 LoggedFlow = FlowSensor;
if LogCounter >= 60 LogCounter = 0;

// Could trigger data transmission
if LoggedTemp > 50 HighTempFlag = 1;
```

## Advanced Features

### Conditional Logic

```javascript
// Multiple conditions
if Temperature > 25 & Humidity < 40 Humidifier = 1;
if Temperature > 25 & Humidity < 40 Fan = 0;

// Nested conditions using multiple if statements
if SystemEnabled TempCheck = 1;
if TempCheck & Temperature < 20 Heater = 1;
if TempCheck & Temperature > 30 Heater = 0;
```

### Pause Functionality

```javascript
// Timed sequences (each statement executes in order)
Valve1 = 1;
pause 5;        // Wait 5 seconds
Valve1 = 0;
Valve2 = 1;
pause 10;       // Wait 10 seconds  
Valve2 = 0;
SequenceProgram = 0; // End program
```

## Best Practices

1. **Use descriptive variable names**: `WaterPump` instead of `P1`
2. **Self-disable one-shot programs**: Always end with `ProgramName = 0;`
3. **Include safety checks**: Monitor for error conditions
4. **Use timers for sequences**: Better than long pause statements
5. **Document your logic**: Use meaningful panel names

## Error Handling

The interpreter will provide error messages for:
- Undefined variables
- Invalid number formats  
- Division by zero
- Missing operands
- Unknown operators

Check the error output to debug your programs!

---

*This interpreter integrates seamlessly with your Firefly GUI panels, making automation programming intuitive and powerful.*